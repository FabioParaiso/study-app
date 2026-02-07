from sqlalchemy.orm import Session
from models import QuizResult, QuestionAnalytics, StudyMaterial


class QuizRepositoryBase:
    def __init__(self, db: Session):
        self.db = db


class QuizResultPersistenceRepository(QuizRepositoryBase):
    def record_quiz_result(
        self,
        student_id: int,
        score: int,
        total: int,
        quiz_type: str,
        analytics_data: list[dict],
        material_id: int | None,
        xp_earned: int,
        duration_seconds: int,
        active_seconds: int
    ) -> int:
        try:
            analytics_data = analytics_data or []
            effective_total = len(analytics_data)
            effective_correct = sum(1 for item in analytics_data if item.get("is_correct"))

            result = QuizResult(
                student_id=student_id,
                study_material_id=material_id,
                score=score,
                total_questions=total,
                quiz_type=quiz_type,
                duration_seconds=max(0, int(duration_seconds or 0)),
                active_seconds=max(0, int(active_seconds or 0))
            )
            self.db.add(result)
            self.db.flush()

            for item in analytics_data:
                concept_name = item.get("topic") or "Geral"
                concept_id = item.get("concept_id")

                analytic = QuestionAnalytics(
                    quiz_result_id=result.id,
                    topic=concept_name,
                    concept_id=concept_id,
                    is_correct=item.get("is_correct")
                )
                self.db.add(analytic)

            if material_id:
                material = self.db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
                if material:
                    material.total_questions_answered += effective_total
                    material.correct_answers_count += effective_correct
                    material.total_xp += xp_earned
                    material.high_score = max(material.high_score, score)

            self.db.commit()
            return int(result.id)
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            self.db.rollback()
            return 0
