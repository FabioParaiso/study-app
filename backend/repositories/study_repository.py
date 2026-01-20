import json
from sqlalchemy.orm import Session
from models import StudyMaterial, QuizResult, QuestionAnalytics, Student

class StudyRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Student Methods ---
    def get_or_create_student(self, name: str) -> Student:
        student = self.db.query(Student).filter(Student.name == name).first()
        if not student:
            student = Student(name=name)
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
        return student

    def get_student(self, student_id: int) -> Student:
        return self.db.query(Student).filter(Student.id == student_id).first()

    # --- Material Methods ---
    def save(self, text: str, source_name: str, topics: list[str] = None) -> StudyMaterial:
        """Saves or updates the single active study material."""
        try:
            # 1. Clear existing (We only support 1 active material for now)
            self.db.query(StudyMaterial).delete()
            
            # 2. Add new
            db_item = StudyMaterial(
                text=text,
                source=source_name,
                topics=json.dumps(topics or [])
            )
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except Exception as e:
            print(f"Error saving material: {e}")
            self.db.rollback()
            return None

    def load(self) -> dict:
        """Loads the study material."""
        try:
            item = self.db.query(StudyMaterial).first()
            if item:
                return {
                    "id": item.id,
                    "text": item.text,
                    "source": item.source,
                    "topics": json.loads(item.topics) if item.topics else []
                }
            return None
        except Exception as e:
            print(f"Error loading material: {e}")
            return None

    def clear(self) -> bool:
        """Deletes the saved study material."""
        try:
            self.db.query(StudyMaterial).delete()
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error clearing material: {e}")
            self.db.rollback()
            return False

    # --- Quiz & Analytics Methods ---
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
                analytic = QuestionAnalytics(
                    quiz_result_id=result.id,
                    topic=item.get("topic") or "Geral",
                    is_correct=item.get("is_correct")
                )
                self.db.add(analytic)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            self.db.rollback()
            return False

    def get_student_analytics(self, student_id: int):
        """Calculates success rate per topic for a specific student."""
        try:
            # Get all analytics for this student
            analytics = (
                self.db.query(QuestionAnalytics)
                .join(QuizResult)
                .filter(QuizResult.student_id == student_id)
                .all()
            )
            
            if not analytics: return []

            stats = {} # {topic: {total: 0, correct: 0}}
            
            for a in analytics:
                if a.topic not in stats:
                    stats[a.topic] = {"total": 0, "correct": 0}
                stats[a.topic]["total"] += 1
                if a.is_correct:
                    stats[a.topic]["correct"] += 1
            
            results = []
            for topic, data in stats.items():
                success_rate = (data["correct"] / data["total"]) * 100
                results.append({
                    "topic": topic,
                    "success_rate": round(success_rate),
                    "total_questions": data["total"]
                })
            
            return sorted(results, key=lambda x: x["success_rate"])
            
        except Exception as e:
            print(f"Error calculating analytics: {e}")
            return []
