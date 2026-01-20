import json
from sqlalchemy.orm import Session
from models import StudyMaterial

class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, student_id: int, text: str, source_name: str, topics: list[str] = None) -> StudyMaterial:
        """Saves or updates the active study material for a specific student."""
        try:
            # 1. Clear existing for this student
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).delete()
            
            # 2. Add new
            db_item = StudyMaterial(
                student_id=student_id,
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

    def load(self, student_id: int) -> dict:
        """Loads the study material for a specific student."""
        try:
            item = self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).first()
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
