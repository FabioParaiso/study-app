import json
from datetime import datetime
from sqlalchemy.orm import Session
from models import StudyMaterial, Student

class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, student_id: int, text: str, source_name: str, topics: dict[str, list[str]] = None) -> StudyMaterial:
        """Saves or updates the study material, setting it as active. Topics is {Topic: [Concepts]}."""
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
                # Clear existing topics to overwrite (cascade should handle it, but explicit clear is safer)
                # We need to delete old topics since we are replacing the structure
                # Actually, cascade="all, delete-orphan" on relationship takes care of it if we replace the list
                # But to replace the list we need to create new objects.
                # db_item.topics = [] # This clears the relationship
                # Let's rebuild properly
                db_item.topics = []
                
                db_item.is_active = True
                db_item.last_accessed = datetime.utcnow()
            else:
                # Create new
                db_item = StudyMaterial(
                    student_id=student_id,
                    text=text,
                    source=source_name,
                    is_active=True,
                    last_accessed=datetime.utcnow() 
                )
                self.db.add(db_item)
            
            # 3. Create Topic and Concept hierarchy
            if topics:
                from models import Topic, Concept
                new_topic_objs = []
                for topic_name, concepts_list in topics.items():
                    topic_obj = Topic(name=topic_name)
                    # Create concepts
                    concept_objs = [Concept(name=c_name) for c_name in concepts_list]
                    topic_obj.concepts = concept_objs
                    new_topic_objs.append(topic_obj)
                
                db_item.topics = new_topic_objs

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
                # Reconstruct dict from relations
                topics_dict = {}
                if item.topics:
                    for topic in item.topics:
                        topics_dict[topic.name] = [c.name for c in topic.concepts]

                return {
                    "id": item.id,
                    "text": item.text,
                    "source": item.source,
                    "topics": topics_dict, # Now returning dict structure
                    # Gamification stats for this material
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
        """Deactivates the current study material (does not delete)."""
        try:
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).update({"is_active": False})
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error clearing material: {e}")
            self.db.rollback()
            return False

    def list_all(self, student_id: int) -> list[dict]:
        """Lists all study materials for a specific student."""
        try:
            items = self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).all()
            return [
                {
                    "id": item.id,
                    "source": item.source,
                    "created_at": item.created_at,
                    "is_active": item.is_active,
                    "preview": item.text[:100] if item.text else "",
                    "total_xp": item.total_xp
                }
                for item in items
            ]
        except Exception as e:
            print(f"Error listing materials: {e}")
            return []

    def activate(self, student_id: int, material_id: int) -> bool:
        """Activates a specific material and deactivates others."""
        try:
            # 1. Deactivate all
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).update({"is_active": False})
            
            # 2. Activate specific
            item = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id, 
                StudyMaterial.id == material_id
            ).first()
            
            if item:
                item.is_active = True
                item.last_accessed = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error activating material: {e}")
            self.db.rollback()
            return False

    def delete(self, student_id: int, material_id: int) -> bool:
        """Permanently deletes a specific material, its history, and deducts associated XP."""
        try:
            # 1. Fetch Material
            material = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.id == material_id
            ).first()
            
            if not material:
                return False

            # 2. Deduct XP from Student
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if student and material.total_xp > 0:
                student.total_xp = max(0, student.total_xp - material.total_xp)

            # 3. Delete associated QuizResults
            # Note: QuizResults might not cascade automatically if not configured, so we do it explicitly
            from models import QuizResult
            self.db.query(QuizResult).filter(
                QuizResult.study_material_id == material_id
            ).delete()

            # 4. Delete Material (Cascades to Topics -> Concepts)
            self.db.delete(material)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting material: {e}")
            self.db.rollback()
            return False
