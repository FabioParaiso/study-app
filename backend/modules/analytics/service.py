import random
from datetime import datetime, timedelta, timezone, time as time_cls
from modules.analytics.calculator import AnalyticsCalculator
from modules.analytics.ports import AnalyticsRepositoryPort
from modules.materials.ports import MaterialConceptPairsRepositoryPort

class AnalyticsService:
    def __init__(self, analytics_repo: AnalyticsRepositoryPort, material_repo: MaterialConceptPairsRepositoryPort):
        self.analytics_repo = analytics_repo
        self.material_repo = material_repo

    def get_weak_points(self, student_id: int, material_id: int = None):
        if material_id:
            concept_pairs = self.material_repo.get_concept_pairs(material_id)
        else:
            concept_pairs = self.material_repo.get_concept_pairs_for_student(student_id)

        analytics_items = self.analytics_repo.fetch_question_analytics(student_id, material_id)
        
        # DEBUG PRINTS
        print(f"DEBUG: get_weak_points material_id={material_id}")
        print(f"DEBUG: concept_pairs={concept_pairs}")
        print(f"DEBUG: analytics_items count={len(analytics_items)}")
        
        return AnalyticsCalculator.build_results(concept_pairs, analytics_items)

    def get_adaptive_topics(self, student_id: int, material_id: int = None):
        analytics = self.get_weak_points(student_id, material_id)
        if not analytics:
            return {"boost": [], "mastered": []}

        def _unique_topics(items: list[str]) -> list[str]:
            seen: set[str] = set()
            unique: list[str] = []
            for topic in items:
                if topic not in seen:
                    seen.add(topic)
                    unique.append(topic)
            return unique

        boost = _unique_topics([item["topic"] for item in analytics if item["success_rate"] < 70])
        mastered = _unique_topics([item["topic"] for item in analytics if item["success_rate"] >= 90])
        
        return {"boost": boost, "mastered": mastered}

    def get_classified_concepts(self, student_id: int, material_id: int | None = None) -> dict[str, list[str]]:
        results = self.get_weak_points(student_id, material_id)
        
        unseen = []
        weak = []
        strong = []
        
        for item in results:
            concept = item["concept"]
            if not concept:
                continue

            mcq_count = item.get("total_questions_mcq", 0)
            effective_mcq = item.get("effective_mcq", 0)

            if mcq_count == 0:
                unseen.append(concept)
            elif effective_mcq <= 75:
                # <= 75% includes "Weak" and "Learning" (Fraco/Em aprendizagem) for MCQ only
                weak.append(concept)
            else:
                # > 75% includes "Strong" (Forte/Ok) for MCQ only
                strong.append(concept)
                
        return {
            "unseen": unseen,
            "weak": weak,
            "strong": strong
        }

    @staticmethod
    def _parse_datetime(value) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None

    @staticmethod
    def _to_local_date(value, tz_offset_minutes: int):
        dt = AnalyticsService._parse_datetime(value)
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        local_dt = dt + timedelta(minutes=tz_offset_minutes)
        return local_dt.date()

    def get_recent_metrics(self, student_id: int, days: int = 30, tz_offset_minutes: int = 0) -> dict:
        safe_days = max(1, min(int(days or 30), 90))
        tz_offset_minutes = int(tz_offset_minutes or 0)

        now_utc = datetime.now(timezone.utc)
        local_now = now_utc + timedelta(minutes=tz_offset_minutes)
        end_local_date = local_now.date()
        start_local_date = end_local_date - timedelta(days=safe_days - 1)

        start_utc = datetime.combine(start_local_date, time_cls.min, tzinfo=timezone.utc) - timedelta(minutes=tz_offset_minutes)
        end_utc = datetime.combine(end_local_date + timedelta(days=1), time_cls.min, tzinfo=timezone.utc) - timedelta(minutes=tz_offset_minutes)

        sessions = self.analytics_repo.fetch_quiz_sessions(student_id, start_utc, end_utc)

        quiz_types = ["multiple-choice", "short_answer", "open-ended"]
        daily_map: dict = {}
        cursor = start_local_date
        while cursor <= end_local_date:
            daily_map[cursor] = {
                "day": cursor.isoformat(),
                "active_seconds": 0,
                "duration_seconds": 0,
                "tests_total": 0,
                "by_type": {qt: 0 for qt in quiz_types},
            }
            cursor += timedelta(days=1)

        for session in sessions:
            local_date = self._to_local_date(session.get("created_at"), tz_offset_minutes)
            if local_date is None or local_date not in daily_map:
                continue

            entry = daily_map[local_date]
            quiz_type = session.get("quiz_type") or "multiple-choice"
            if quiz_type not in entry["by_type"]:
                entry["by_type"][quiz_type] = 0
            entry["by_type"][quiz_type] += 1
            entry["tests_total"] += 1
            entry["active_seconds"] += max(0, int(session.get("active_seconds") or 0))
            entry["duration_seconds"] += max(0, int(session.get("duration_seconds") or 0))

        daily = [daily_map[d] for d in sorted(daily_map.keys())]

        totals_by_type = {qt: 0 for qt in quiz_types}
        total_active = 0
        total_duration = 0
        total_tests = 0
        goal_seconds = 30 * 60
        days_with_goal = 0

        for entry in daily:
            total_active += entry["active_seconds"]
            total_duration += entry["duration_seconds"]
            total_tests += entry["tests_total"]
            if entry["active_seconds"] >= goal_seconds:
                days_with_goal += 1
            for qt, count in entry["by_type"].items():
                totals_by_type[qt] = totals_by_type.get(qt, 0) + count

        return {
            "range": {
                "start": start_local_date.isoformat(),
                "end": end_local_date.isoformat(),
                "days": safe_days,
                "tz_offset_minutes": tz_offset_minutes
            },
            "daily": daily,
            "totals": {
                "active_seconds": total_active,
                "duration_seconds": total_duration,
                "tests_total": total_tests,
                "by_type": totals_by_type,
                "days_with_goal": days_with_goal,
                "goal_seconds": goal_seconds
            }
        }

    def build_mcq_quiz_concepts(
        self,
        student_id: int,
        material_id: int | None = None,
        allowed_concepts: set[str] | None = None,
        total_questions: int = 10
    ) -> list[str]:
        results = self.get_weak_points(student_id, material_id)

        items: list[dict] = []
        for item in results:
            concept = item.get("concept")
            if not concept:
                continue
            if allowed_concepts and concept not in allowed_concepts:
                continue
            items.append({
                "concept": concept,
                "effective_mcq": item.get("effective_mcq", 0),
                "total_questions_mcq": item.get("total_questions_mcq", 0),
            })

        if not items or total_questions <= 0:
            return []

        unseen_items = [i for i in items if i["total_questions_mcq"] == 0]
        weak_items = [i for i in items if i["total_questions_mcq"] > 0 and i["effective_mcq"] <= 75]
        strong_items = [i for i in items if i["total_questions_mcq"] > 0 and i["effective_mcq"] > 75]

        unseen_items = sorted(unseen_items, key=lambda i: i["concept"].lower())
        weak_items = sorted(weak_items, key=lambda i: (i["effective_mcq"], i["concept"].lower()))
        strong_items = sorted(strong_items, key=lambda i: (i["effective_mcq"], i["concept"].lower()))

        def _repeat_by_weight(
            bucket: list[dict],
            count: int,
            weight_fn=None,
            ensure_each_once: bool = True
        ) -> list[str]:
            if count <= 0 or not bucket:
                return []

            concepts = [i["concept"] for i in bucket]
            if ensure_each_once and count <= len(concepts):
                return concepts[:count]

            selected: list[str] = []
            remaining = count
            if ensure_each_once:
                selected = concepts[:]
                remaining = count - len(concepts)

            if remaining <= 0:
                return selected

            if weight_fn is None:
                idx = 0
                while remaining > 0:
                    selected.append(concepts[idx % len(concepts)])
                    idx += 1
                    remaining -= 1
                return selected

            weights = [max(1, int(weight_fn(i))) for i in bucket]
            total_weight = sum(weights)
            allocations = [int((w / total_weight) * remaining) for w in weights]
            allocated = sum(allocations)
            remainder = remaining - allocated
            order = sorted(
                range(len(bucket)),
                key=lambda i: (-weights[i], concepts[i].lower())
            )
            for i in range(remainder):
                allocations[order[i % len(order)]] += 1
            for idx, count in enumerate(allocations):
                if count > 0:
                    selected.extend([concepts[idx]] * count)
            return selected

        def _fill(bucket: list[dict], count: int, weight_fn=None) -> tuple[list[str], int]:
            if count <= 0:
                return [], 0
            if not bucket:
                return [], count
            return _repeat_by_weight(bucket, count, weight_fn=weight_fn, ensure_each_once=True), 0

        def _weak_weight(item: dict) -> int:
            return max(1, 100 - int(item.get("effective_mcq", 0)))

        selected: list[str] = []
        shortage = 0

        unseen_selected, shortage = _fill(unseen_items, 5)
        selected.extend(unseen_selected)

        weak_selected, shortage = _fill(weak_items, 4 + shortage, weight_fn=_weak_weight)
        selected.extend(weak_selected)

        strong_selected, shortage = _fill(strong_items, 1 + shortage)
        selected.extend(strong_selected)

        if shortage > 0:
            fallback_bucket = weak_items or unseen_items or strong_items
            if fallback_bucket:
                fallback_weight = _weak_weight if fallback_bucket is weak_items else None
                selected.extend(
                    _repeat_by_weight(
                        fallback_bucket,
                        shortage,
                        weight_fn=fallback_weight,
                        ensure_each_once=False
                    )
                )

        selected = selected[:total_questions]
        random.shuffle(selected)
        return selected
