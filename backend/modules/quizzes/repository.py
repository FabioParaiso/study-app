from sqlalchemy.orm import Session
from models import QuizResult, QuestionAnalytics

class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_quiz_result(self, student_id: int, score: int, total: int, quiz_type: str, analytics_data: list[dict], material_id: int = None):
        """Saves quiz result and granular analytics."""
        try:
            result = QuizResult(
                student_id=student_id,
                study_material_id=material_id,
                score=score, 
                total_questions=total, 
                quiz_type=quiz_type
            )
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            
            for item in analytics_data:
                concept_name = item.get("topic") or "Geral"
                concept_id = item.get("concept_id")

                analytic = QuestionAnalytics(
                    quiz_result_id=result.id,
                    topic=concept_name, # Stores Concept Name
                    concept_id=concept_id,
                    is_correct=item.get("is_correct")
                )
                self.db.add(analytic)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            self.db.rollback()
            return False

    def delete_results_for_material(self, material_id: int) -> int:
        """Deletes quiz results linked to a material and returns count."""
        try:
            count = (
                self.db.query(QuizResult)
                .filter(QuizResult.study_material_id == material_id)
                .delete()
            )
            self.db.commit()
            return count or 0
        except Exception as e:
            print(f"Error deleting quiz results: {e}")
            self.db.rollback()
            return 0

    # get_all_topics removed: aggregate topic lists should be composed in services using material + analytics sources.
