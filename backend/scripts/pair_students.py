from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any

from sqlalchemy import bindparam, inspect, text
from sqlalchemy.orm import Session

from database import SessionLocal


@dataclass
class StudentSelector:
    student_id: int | None = None
    student_name: str | None = None


def _has_column(db: Session, table_name: str, column_name: str) -> bool:
    inspector = inspect(db.bind)
    return column_name in {col["name"] for col in inspector.get_columns(table_name)}


def _resolve_student(db: Session, selector: StudentSelector) -> dict[str, Any]:
    if selector.student_id is not None:
        row = db.execute(
            text("SELECT id, name, partner_id FROM students WHERE id = :id"),
            {"id": int(selector.student_id)},
        ).mappings().first()
    elif selector.student_name:
        row = db.execute(
            text("SELECT id, name, partner_id FROM students WHERE name = :name"),
            {"name": selector.student_name},
        ).mappings().first()
    else:
        raise ValueError("Student selector must include id or name.")

    if row is None:
        if selector.student_id is not None:
            raise ValueError(f"Student not found for id={selector.student_id}")
        raise ValueError(f"Student not found for name={selector.student_name}")
    return dict(row)


def _collect_ids_to_clear(db: Session, a_id: int, b_id: int, a_partner: int | None, b_partner: int | None) -> list[int]:
    ids = {a_id, b_id}
    if a_partner:
        ids.add(int(a_partner))
    if b_partner:
        ids.add(int(b_partner))

    rows_pointing_ab = db.execute(
        text("SELECT id FROM students WHERE partner_id IN (:a_id, :b_id)"),
        {"a_id": a_id, "b_id": b_id},
    ).mappings().all()
    for row in rows_pointing_ab:
        ids.add(int(row["id"]))

    if a_partner or b_partner:
        partners = [pid for pid in (a_partner, b_partner) if pid is not None]
        stmt = text("SELECT id FROM students WHERE partner_id IN :partner_ids").bindparams(
            bindparam("partner_ids", expanding=True)
        )
        rows_pointing_partners = db.execute(
            stmt,
            {"partner_ids": [int(pid) for pid in partners]},
        ).mappings().all()
        for row in rows_pointing_partners:
            ids.add(int(row["id"]))

    return sorted(ids)


def run_pairing(
    db: Session,
    a_selector: StudentSelector,
    b_selector: StudentSelector,
    apply: bool = False,
) -> dict[str, Any]:
    if not _has_column(db, "students", "partner_id"):
        raise RuntimeError(
            "Column students.partner_id not found. Run this script only after Sprint 1A migration."
        )

    a = _resolve_student(db, a_selector)
    b = _resolve_student(db, b_selector)
    a_id = int(a["id"])
    b_id = int(b["id"])
    if a_id == b_id:
        raise ValueError("Cannot pair a student with themselves.")

    ids_to_clear = _collect_ids_to_clear(
        db,
        a_id=a_id,
        b_id=b_id,
        a_partner=a.get("partner_id"),
        b_partner=b.get("partner_id"),
    )

    if apply:
        clear_stmt = text("UPDATE students SET partner_id = NULL WHERE id IN :ids").bindparams(
            bindparam("ids", expanding=True)
        )
        clear_refs_stmt = text("UPDATE students SET partner_id = NULL WHERE partner_id IN :ids").bindparams(
            bindparam("ids", expanding=True)
        )
        try:
            db.execute(
                clear_stmt,
                {"ids": [int(sid) for sid in ids_to_clear]},
            )
            db.execute(
                clear_refs_stmt,
                {"ids": [int(sid) for sid in ids_to_clear]},
            )
            db.execute(
                text("UPDATE students SET partner_id = :b_id WHERE id = :a_id"),
                {"a_id": a_id, "b_id": b_id},
            )
            db.execute(
                text("UPDATE students SET partner_id = :a_id WHERE id = :b_id"),
                {"a_id": a_id, "b_id": b_id},
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

    return {
        "dry_run": not apply,
        "student_a": {"id": a_id, "name": a["name"], "current_partner_id": a.get("partner_id")},
        "student_b": {"id": b_id, "name": b["name"], "current_partner_id": b.get("partner_id")},
        "pair_after": {"a_partner_id": b_id, "b_partner_id": a_id},
        "ids_cleared_before_pairing": ids_to_clear,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pair two students symmetrically.")

    parser.add_argument("--dry-run", action="store_true", help="Do not write DB changes.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")

    group_a = parser.add_mutually_exclusive_group(required=True)
    group_a.add_argument("--a-id", type=int)
    group_a.add_argument("--a-name")

    group_b = parser.add_mutually_exclusive_group(required=True)
    group_b.add_argument("--b-id", type=int)
    group_b.add_argument("--b-name")
    return parser


def _print_human(result: dict[str, Any]) -> None:
    mode = "DRY-RUN" if result["dry_run"] else "APPLY"
    a = result["student_a"]
    b = result["student_b"]
    print(f"[{mode}] Pair students")
    print(
        f"A: id={a['id']} name={a['name']} current_partner_id={a['current_partner_id']} -> {result['pair_after']['a_partner_id']}"
    )
    print(
        f"B: id={b['id']} name={b['name']} current_partner_id={b['current_partner_id']} -> {result['pair_after']['b_partner_id']}"
    )
    print(f"Cleared IDs before pairing: {result['ids_cleared_before_pairing']}")


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    a_selector = StudentSelector(student_id=args.a_id, student_name=args.a_name)
    b_selector = StudentSelector(student_id=args.b_id, student_name=args.b_name)

    db = SessionLocal()
    try:
        result = run_pairing(db=db, a_selector=a_selector, b_selector=b_selector, apply=not args.dry_run)
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
