from sqlalchemy.orm import Session
from models import QuizResult, QuestionAnalytics, Concept, Topic


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def fetch_question_analytics(self, student_id: int, material_id: int | None = None) -> list[dict]:
        """Returns analytics records with resolved concept/topic names."""
        try:
            query = (
                self.db.query(
                    QuestionAnalytics.is_correct,
                    QuestionAnalytics.topic.label("raw_concept"),
                    Concept.name.label("concept_name"),
                    Topic.name.label("topic_name"),
                    QuizResult.created_at, # Added timestamp
                    QuizResult.quiz_type,
                )
                .join(QuizResult, QuestionAnalytics.quiz_result_id == QuizResult.id)
                .outerjoin(Concept, QuestionAnalytics.concept_id == Concept.id)
                .outerjoin(Topic, Concept.topic_id == Topic.id)
                .filter(QuizResult.student_id == student_id)
            )
            if material_id:
                query = query.filter(QuizResult.study_material_id == material_id)

            rows = query.all()
            return [
                {
                    "is_correct": row.is_correct,
                    "raw_concept": row.raw_concept,
                    "concept_name": row.concept_name,
                    "topic_name": row.topic_name,
                    "created_at": row.created_at, # Added timestamp
                    "quiz_type": row.quiz_type,
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error fetching analytics records: {e}")
            return []

    def fetch_quiz_sessions(self, student_id: int, start_utc, end_utc) -> list[dict]:
        """Returns quiz sessions for a student within [start_utc, end_utc)."""
        try:
            rows = (
                self.db.query(
                    QuizResult.created_at,
                    QuizResult.quiz_type,
                    QuizResult.duration_seconds,
                    QuizResult.active_seconds,
                )
                .filter(
                    QuizResult.student_id == student_id,
                    QuizResult.created_at >= start_utc,
                    QuizResult.created_at < end_utc,
                )
                .all()
            )
            return [
                {
                    "created_at": row.created_at,
                    "quiz_type": row.quiz_type,
                    "duration_seconds": row.duration_seconds,
                    "active_seconds": row.active_seconds,
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error fetching quiz sessions: {e}")
            return []
