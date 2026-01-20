import json
from datetime import datetime
from sqlalchemy.orm import Session
from models import StudyMaterial

class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, student_id: int, text: str, source_name: str, topics: list[str] = None) -> StudyMaterial:
        """Saves or updates the study material, setting it as active."""
        try:
            # 1. Deactivate all existing materials for this student
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).update({"is_active": False})
            
            # 2. Check if material with same source exists
            db_item = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.source == source_name
            ).first()

            if db_item:
                # Update existing
                db_item.text = text
                if topics:
                    db_item.topics = json.dumps(topics)
                db_item.is_active = True
                db_item.last_accessed = datetime.utcnow()
            else:
                # Create new
                db_item = StudyMaterial(
                    student_id=student_id,
                    text=text,
                    source=source_name,
                    topics=json.dumps(topics or []),
                    is_active=True,
                    last_accessed=datetime.utcnow() # distinct from created_at
                )
                self.db.add(db_item)

            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except Exception as e:
            print(f"Error saving material: {e}")
            self.db.rollback()
            return None

    def load(self, student_id: int) -> dict:
        """Loads the ACTIVE study material for a specific student."""
        try:
            item = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.is_active == True
            ).first()
            
            if item:
                return {
                    "id": item.id,
                    "text": item.text,
                    "source": item.source,
                    "topics": json.loads(item.topics) if item.topics else [],
                    # Return scoped gamification stats
                    "total_xp": item.total_xp,
                    "high_score": item.high_score,
                    "total_questions_answered": item.total_questions_answered,
                    "correct_answers_count": item.correct_answers_count
                }
            return None
            return None
        except Exception as e:
            print(f"Error loading material: {e}")
            return None

    def clear(self, student_id: int) -> bool:
        """Deletes the saved study material for a specific student."""
        try:
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).delete()
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error clearing material: {e}")
            self.db.rollback()
            return False
