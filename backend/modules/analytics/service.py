import random
from collections import deque
from datetime import datetime, timedelta, timezone, time as time_cls
from modules.analytics.calculator import AnalyticsCalculator, _calculate_mastery_simple
from modules.analytics.constants import QUIZ_TYPES, CONFIDENCE_WINDOW
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
        
        return AnalyticsCalculator.build_results(concept_pairs, analytics_items)

    def get_adaptive_topics(self, student_id: int, material_id: int = None):
        analytics = self.get_weak_points(student_id, material_id)
        if not analytics:
            return {"boost": [], "mastered": []}

        boost = []
        mastered = []
        
        for item in analytics:
            topic = item["topic"]
            
            # Only use established MCQ scores for adaptive topics
            mcq_data = item.get("score_data_mcq", {})
            if mcq_data.get("confidence_level") != "established":
                continue
            
            score = (mcq_data.get("score") or 0) * 100
            
            if score < 70:
                boost.append(topic)
            elif score >= 90:
                mastered.append(topic)
        
        return {"boost": self._unique_topics(boost), "mastered": self._unique_topics(mastered)}

    @staticmethod
    def _unique_topics(items: list[str]) -> list[str]:
        """Return unique items preserving order."""
        seen: set[str] = set()
        return [x for x in items if not (x in seen or seen.add(x))]

    def get_classified_concepts(self, student_id: int, material_id: int | None = None) -> dict[str, list[str]]:
        results = self.get_weak_points(student_id, material_id)
        
        unseen = []
        weak = []
        strong = []
        
        for item in results:
            concept = item["concept"]
            if not concept:
                continue

            mcq_data = item.get("score_data_mcq", {})
            confidence_level = mcq_data.get("confidence_level", "not_seen")
            
            # Exploring and not_seen count as unseen
            if confidence_level in ("not_seen", "exploring"):
                unseen.append(concept)
            else:
                # Building or established - use actual score
                score = (mcq_data.get("score") or 0) * 100
                if score <= 75:
                    weak.append(concept)
                else:
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

        quiz_types = QUIZ_TYPES
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
        for entry in daily:
            total_active += entry["active_seconds"]
            total_duration += entry["duration_seconds"]
            total_tests += entry["tests_total"]
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
                "by_type": totals_by_type
            }
        }

    def get_learning_trend(
        self,
        student_id: int,
        days: int = 30,
        tz_offset_minutes: int = 0,
        min_questions: int = 1
    ) -> dict:
        safe_days = max(1, min(int(days or 30), 90))
        tz_offset_minutes = int(tz_offset_minutes or 0)
        min_questions = max(1, int(min_questions or 1))

        now_utc = datetime.now(timezone.utc)
        local_now = now_utc + timedelta(minutes=tz_offset_minutes)
        end_local_date = local_now.date()
        start_local_date = end_local_date - timedelta(days=safe_days - 1)

        end_utc = datetime.combine(end_local_date + timedelta(days=1), time_cls.min, tzinfo=timezone.utc) - timedelta(minutes=tz_offset_minutes)

        items = self.analytics_repo.fetch_question_analytics(student_id, None)

        quiz_types = QUIZ_TYPES
        events_by_day: dict = {}

        for item in items:
            dt = self._parse_datetime(item.get("created_at"))
            if dt is None:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(timezone.utc)
            if dt >= end_utc:
                continue

            quiz_type = item.get("quiz_type") or "multiple-choice"
            if quiz_type not in quiz_types:
                continue

            concept_id = item.get("concept_id")
            if concept_id:
                concept_key = ("id", concept_id)
            else:
                raw_name = item.get("concept_name") or item.get("raw_concept") or "Geral"
                norm_name = raw_name.strip().lower()
                if not norm_name:
                    norm_name = "geral"
                concept_key = ("name", norm_name)

            local_date = (dt + timedelta(minutes=tz_offset_minutes)).date()
            events_by_day.setdefault(local_date, []).append({
                "dt": dt,
                "quiz_type": quiz_type,
                "is_correct": bool(item.get("is_correct")),
                "concept_key": concept_key
            })

        for day_events in events_by_day.values():
            day_events.sort(key=lambda e: e["dt"])

        state: dict = {qt: {} for qt in quiz_types}

        def _update_state(event: dict):
            qt = event["quiz_type"]
            concept_key = event["concept_key"]
            if concept_key not in state[qt]:
                state[qt][concept_key] = {
                    "window": deque(maxlen=CONFIDENCE_WINDOW),
                    "total": 0,
                    "effective": 0.0
                }
            entry = state[qt][concept_key]
            entry["window"].append(event["is_correct"])
            entry["total"] += 1
            # Convert deque to list of dicts for mastery calculation
            window_items = [{"is_correct": v} for v in entry["window"]]
            entry["effective"] = _calculate_mastery_simple(window_items, CONFIDENCE_WINDOW)

        pre_days = sorted(d for d in events_by_day.keys() if d < start_local_date)
        for day in pre_days:
            for event in events_by_day[day]:
                _update_state(event)

        daily = []
        cursor = start_local_date
        while cursor <= end_local_date:
            day_events = events_by_day.get(cursor, [])
            day_counts = {qt: 0 for qt in quiz_types}

            for event in day_events:
                _update_state(event)
                day_counts[event["quiz_type"]] += 1

            by_level = {}
            for qt in quiz_types:
                if day_counts[qt] < min_questions:
                    value = None
                else:
                    seen = [s for s in state[qt].values() if s["total"] > 0]
                    if not seen:
                        value = None
                    else:
                        avg = sum(s["effective"] for s in seen) / len(seen)
                        value = round(avg * 100)
                by_level[qt] = {
                    "value": value,
                    "questions": day_counts[qt]
                }

            daily.append({
                "day": cursor.isoformat(),
                "by_level": by_level
            })

            cursor += timedelta(days=1)

        return {
            "range": {
                "start": start_local_date.isoformat(),
                "end": end_local_date.isoformat(),
                "days": safe_days,
                "tz_offset_minutes": tz_offset_minutes,
                "min_questions": min_questions
            },
            "daily": daily
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
            
            mcq_data = item.get("score_data_mcq", {})
            confidence_level = mcq_data.get("confidence_level", "not_seen")
            score_pct = round((mcq_data.get("score") or 0) * 100)
            
            items.append({
                "concept": concept,
                "effective_mcq": score_pct,
                "confidence_level": confidence_level,
                "total_questions_mcq": item.get("total_questions_mcq", 0),
            })

        if not items or total_questions <= 0:
            return []

        # Treat "not_seen" and "exploring" as unseen
        unseen_items = [i for i in items if i["confidence_level"] in ("not_seen", "exploring")]
        weak_items = [i for i in items if i["confidence_level"] not in ("not_seen", "exploring") and i["effective_mcq"] <= 75]
        strong_items = [i for i in items if i["confidence_level"] not in ("not_seen", "exploring") and i["effective_mcq"] > 75]

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
