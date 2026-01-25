from datetime import datetime
from sqlalchemy.orm import Session
from models import StudyMaterial

class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def deactivate_all(self, student_id: int, commit: bool = True) -> bool:
        """Deactivates all materials for a student."""
        try:
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).update({"is_active": False})
            if commit:
                self.db.commit()
            return True
        except Exception as e:
            print(f"Error deactivating materials: {e}")
            self.db.rollback()
            return False

    def find_by_source(self, student_id: int, source_name: str) -> StudyMaterial | None:
        """Fetch material by source for a student."""
        try:
            return self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.source == source_name
            ).first()
        except Exception as e:
            print(f"Error finding material by source: {e}")
            return None

    def save_material(self, material: StudyMaterial) -> StudyMaterial | None:
        """Persists a material instance (with topics attached)."""
        try:
            self.db.add(material)
            self.db.commit()
            self.db.refresh(material)
            return material
        except Exception as e:
            print(f"Error saving material: {e}")
            self.db.rollback()
            return None

    def load(self, student_id: int) -> StudyMaterial | None:
        """Loads the ACTIVE study material for a specific student."""
        try:
            return self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.is_active == True
            ).first()
        except Exception as e:
            print(f"Error loading material: {e}")
            return None

    def get_stats(self, student_id: int, material_id: int) -> dict:
        """Fetches material stats for a specific student/material pair."""
        try:
            item = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.id == material_id
            ).first()
            if not item:
                return None
            return {
                "id": item.id,
                "total_xp": item.total_xp,
                "high_score": item.high_score,
                "total_questions_answered": item.total_questions_answered,
                "correct_answers_count": item.correct_answers_count
            }
        except Exception as e:
            print(f"Error loading material stats: {e}")
            return None

    def get_stats_by_id(self, material_id: int) -> dict:
        """Fetches material stats by material id (no ownership check)."""
        try:
            item = self.db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
            if not item:
                return None
            return {
                "id": item.id,
                "total_xp": item.total_xp,
                "high_score": item.high_score,
                "total_questions_answered": item.total_questions_answered,
                "correct_answers_count": item.correct_answers_count
            }
        except Exception as e:
            print(f"Error loading material stats: {e}")
            return None

    def get_concept_id_map(self, material_id: int) -> dict[str, int]:
        """Returns a map of normalized concept name -> concept id for a material."""
        try:
            from models import Concept, Topic

            rows = (
                self.db.query(Concept.id, Concept.name)
                .join(Topic)
                .filter(Topic.study_material_id == material_id)
                .all()
            )
            concept_map: dict[str, int] = {}
            for concept_id, concept_name in rows:
                key = concept_name.strip().lower()
                if key and key not in concept_map:
                    concept_map[key] = concept_id
            return concept_map
        except Exception as e:
            print(f"Error loading concept map: {e}")
            return {}

    def get_concept_pairs(self, material_id: int) -> list[tuple[str, str]]:
        """Returns [(topic_name, concept_name)] for a material."""
        try:
            from models import Topic, Concept

            rows = (
                self.db.query(Topic.name, Concept.name)
                .join(Concept, Concept.topic_id == Topic.id)
                .filter(Topic.study_material_id == material_id)
                .all()
            )
            return [(t_name, c_name) for t_name, c_name in rows]
        except Exception as e:
            print(f"Error loading concept pairs: {e}")
            return []

    def get_concept_pairs_for_student(self, student_id: int) -> list[tuple[str, str]]:
        """Returns [(topic_name, concept_name)] for all materials of a student."""
        try:
            from models import StudyMaterial, Topic, Concept

            rows = (
                self.db.query(Topic.name, Concept.name)
                .join(StudyMaterial, Topic.study_material_id == StudyMaterial.id)
                .join(Concept, Concept.topic_id == Topic.id)
                .filter(StudyMaterial.student_id == student_id)
                .all()
            )
            return [(t_name, c_name) for t_name, c_name in rows]
        except Exception as e:
            print(f"Error loading student concept pairs: {e}")
            return []

    def set_stats(self, material_id: int, total_questions_answered: int, correct_answers_count: int, total_xp: int, high_score: int) -> bool:
        """Persists computed stats for a material."""
        try:
            item = self.db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
            if not item:
                return False
            item.total_questions_answered = total_questions_answered
            item.correct_answers_count = correct_answers_count
            item.total_xp = total_xp
            item.high_score = high_score
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error updating material stats: {e}")
            self.db.rollback()
            return False

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

    def list_all(self, student_id: int) -> list[StudyMaterial]:
        """Lists all study materials for a specific student."""
        try:
            return self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).all()
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
        """Permanently deletes a specific material."""
        try:
            # 1. Fetch Material
            material = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.id == material_id
            ).first()
            
            if not material:
                return False

            # Delete Material (Cascades to Topics -> Concepts)
            self.db.delete(material)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting material: {e}")
            self.db.rollback()
            return False
