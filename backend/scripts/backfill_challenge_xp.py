from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import bindparam, inspect, text
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from modules.challenges.calendar import get_local_date, validate_tz_offset


MIN_ACTIVE_SECONDS = 180
MIN_TOTAL_QUESTIONS = 5
XP_BASE_VALID_DAY = 20
XP_QUALITY_BONUS = 5


@dataclass
class StudentBackfill:
    id: int
    name: str
    tz_offset_minutes: int


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return None
    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _clamp_score_0_100(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(100.0, score))


def _score_pct(row: dict[str, Any]) -> float:
    quiz_type = str(row.get("quiz_type") or "").strip().lower()
    if quiz_type == "multiple-choice":
        total = int(row.get("total_questions") or 0)
        if total <= 0:
            return 0.0
        score = float(row.get("score") or 0)
        return _clamp_score_0_100((score / total) * 100.0)
    return _clamp_score_0_100(row.get("score") or 0)


def _is_valid_session(row: dict[str, Any]) -> bool:
    active_seconds = int(row.get("active_seconds") or 0)
    total_questions = int(row.get("total_questions") or 0)
    return active_seconds >= MIN_ACTIVE_SECONDS and total_questions >= MIN_TOTAL_QUESTIONS


def _load_students(
    db: Session,
    student_ids: list[int],
    student_names: list[str],
    default_tz_offset: int,
    force_tz_offset: int | None,
) -> list[StudentBackfill]:
    inspector = inspect(db.bind)
    columns = {col["name"] for col in inspector.get_columns("students")}
    has_expected_tz = "expected_tz_offset" in columns

    if has_expected_tz:
        rows = db.execute(
            text(
                "SELECT id, name, expected_tz_offset FROM students ORDER BY id ASC"
            )
        ).mappings().all()
    else:
        rows = db.execute(
            text("SELECT id, name FROM students ORDER BY id ASC")
        ).mappings().all()

    selected: list[StudentBackfill] = []
    selected_ids_set = set(student_ids)
    selected_names_set = {name.strip() for name in student_names}
    use_filter = bool(selected_ids_set or selected_names_set)

    all_by_id = {int(row["id"]): row for row in rows}
    all_by_name = {str(row["name"]): row for row in rows}

    missing_ids = [sid for sid in selected_ids_set if sid not in all_by_id]
    missing_names = [name for name in selected_names_set if name not in all_by_name]
    if missing_ids:
        raise ValueError(f"Unknown student id(s): {sorted(missing_ids)}")
    if missing_names:
        raise ValueError(f"Unknown student name(s): {sorted(missing_names)}")

    for row in rows:
        sid = int(row["id"])
        sname = str(row["name"])
        if use_filter and sid not in selected_ids_set and sname not in selected_names_set:
            continue

        if force_tz_offset is not None:
            tz_offset = force_tz_offset
        elif has_expected_tz:
            tz_offset = int(row.get("expected_tz_offset") or default_tz_offset)
        else:
            tz_offset = default_tz_offset

        selected.append(
            StudentBackfill(
                id=sid,
                name=sname,
                tz_offset_minutes=validate_tz_offset(tz_offset, fallback=default_tz_offset),
            )
        )

    return selected


def _load_quiz_rows(db: Session, student_ids: list[int]) -> list[dict[str, Any]]:
    if not student_ids:
        return []
    stmt = text(
        """
        SELECT id, student_id, score, total_questions, quiz_type, active_seconds, created_at
        FROM quiz_results
        WHERE student_id IN :student_ids
        ORDER BY created_at ASC, id ASC
        """
    ).bindparams(bindparam("student_ids", expanding=True))
    rows = db.execute(
        stmt,
        {"student_ids": [int(sid) for sid in student_ids]},
    ).mappings().all()
    return [dict(row) for row in rows]


def _compute_student_xp(
    quiz_rows: list[dict[str, Any]],
    tz_offset_minutes: int,
) -> dict[str, Any]:
    per_day: dict[Any, dict[str, Any]] = defaultdict(lambda: {"best_score_pct": 0.0, "valid_count": 0})
    total_valid_sessions = 0

    for row in quiz_rows:
        if not _is_valid_session(row):
            continue
        dt = _parse_dt(row.get("created_at"))
        if dt is None:
            continue
        day = get_local_date(dt, tz_offset_minutes)
        total_valid_sessions += 1

        entry = per_day[day]
        entry["valid_count"] += 1
        entry["best_score_pct"] = max(entry["best_score_pct"], _score_pct(row))

    active_days = len(per_day)
    quality_days = sum(1 for entry in per_day.values() if entry["best_score_pct"] >= 80.0)
    computed_xp = (active_days * XP_BASE_VALID_DAY) + (quality_days * XP_QUALITY_BONUS)

    return {
        "active_days": active_days,
        "quality_days": quality_days,
        "valid_sessions": total_valid_sessions,
        "computed_xp": computed_xp,
    }


def _has_column(db: Session, table_name: str, column_name: str) -> bool:
    inspector = inspect(db.bind)
    return column_name in {col["name"] for col in inspector.get_columns(table_name)}


def run_backfill(
    db: Session,
    student_ids: list[int],
    student_names: list[str],
    default_tz_offset: int = 0,
    force_tz_offset: int | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    default_tz_offset = validate_tz_offset(default_tz_offset, fallback=0)
    if force_tz_offset is not None:
        force_tz_offset = validate_tz_offset(force_tz_offset, fallback=default_tz_offset)

    students = _load_students(
        db=db,
        student_ids=student_ids,
        student_names=student_names,
        default_tz_offset=default_tz_offset,
        force_tz_offset=force_tz_offset,
    )
    ids = [s.id for s in students]
    rows = _load_quiz_rows(db, ids)
    rows_by_student: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_student[int(row["student_id"])].append(row)

    results: list[dict[str, Any]] = []
    for student in students:
        student_rows = rows_by_student.get(student.id, [])
        metrics = _compute_student_xp(student_rows, student.tz_offset_minutes)
        results.append(
            {
                "student_id": student.id,
                "student_name": student.name,
                "tz_offset_minutes": student.tz_offset_minutes,
                "quiz_results_total": len(student_rows),
                "valid_sessions": metrics["valid_sessions"],
                "active_days": metrics["active_days"],
                "quality_days": metrics["quality_days"],
                "computed_challenge_xp": metrics["computed_xp"],
            }
        )

    if apply:
        if not _has_column(db, "students", "challenge_xp"):
            raise RuntimeError(
                "Column students.challenge_xp not found. Run this with --apply only after Sprint 1A migration."
            )

        try:
            for item in results:
                db.execute(
                    text("UPDATE students SET challenge_xp = :xp WHERE id = :student_id"),
                    {"xp": int(item["computed_challenge_xp"]), "student_id": int(item["student_id"])},
                )
            db.commit()
        except Exception:
            db.rollback()
            raise

    summary = {
        "students_processed": len(results),
        "total_computed_xp": sum(int(item["computed_challenge_xp"]) for item in results),
    }
    return {
        "dry_run": not apply,
        "students": results,
        "summary": summary,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backfill challenge_xp from historical quiz results.")
    parser.add_argument("--apply", action="store_true", help="Persist computed challenge_xp to students table.")
    parser.add_argument("--student-id", type=int, action="append", default=[], help="Student ID filter (repeatable).")
    parser.add_argument("--student-name", action="append", default=[], help="Student name filter (repeatable).")
    parser.add_argument("--default-tz-offset", type=int, default=0, help="Default tz offset minutes when missing.")
    parser.add_argument("--force-tz-offset", type=int, default=None, help="Force tz offset for all selected students.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    return parser


def _print_human(result: dict[str, Any]) -> None:
    mode = "DRY-RUN" if result["dry_run"] else "APPLY"
    print(f"[{mode}] Backfill challenge_xp")
    for item in result["students"]:
        print(
            "- id={student_id} name={student_name} tz={tz_offset_minutes} "
            "results={quiz_results_total} valid={valid_sessions} days={active_days} "
            "quality_days={quality_days} challenge_xp={computed_challenge_xp}".format(**item)
        )
    print(
        "Summary: students_processed={students_processed} total_computed_xp={total_computed_xp}".format(
            **result["summary"]
        )
    )


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = run_backfill(
            db=db,
            student_ids=args.student_id,
            student_names=args.student_name,
            default_tz_offset=args.default_tz_offset,
            force_tz_offset=args.force_tz_offset,
            apply=args.apply,
        )
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        db.close()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
