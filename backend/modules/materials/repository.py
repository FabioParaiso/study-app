from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import StudyMaterial


class MaterialRepositoryBase:
    def __init__(self, db: Session):
        self.db = db


class MaterialUpsertRepository(MaterialRepositoryBase):
    def deactivate_all(self, student_id: int, commit: bool = True) -> bool:
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
        try:
            return self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.source == source_name
            ).first()
        except Exception as e:
            print(f"Error finding material by source: {e}")
            return None

    def save_material(self, material: StudyMaterial) -> StudyMaterial | None:
        try:
            self.db.add(material)
            self.db.commit()
            self.db.refresh(material)
            return material
        except Exception as e:
            print(f"Error saving material: {e}")
            self.db.rollback()
            return None


class MaterialReadRepository(MaterialRepositoryBase):
    def load(self, student_id: int) -> StudyMaterial | None:
        try:
            return self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.is_active == True
            ).first()
        except Exception as e:
            print(f"Error loading material: {e}")
            return None

    def list_all(self, student_id: int) -> list[StudyMaterial]:
        try:
            return self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).all()
        except Exception as e:
            print(f"Error listing materials: {e}")
            return []

    def activate(self, student_id: int, material_id: int) -> bool:
        try:
            item = self.db.query(StudyMaterial).filter(
                StudyMaterial.student_id == student_id,
                StudyMaterial.id == material_id
            ).first()

            if item:
                self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).update({"is_active": False})
                item.is_active = True
                item.last_accessed = datetime.now(timezone.utc)
                self.db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error activating material: {e}")
            self.db.rollback()
            return False

    def clear(self, student_id: int) -> bool:
        try:
            self.db.query(StudyMaterial).filter(StudyMaterial.student_id == student_id).update({"is_active": False})
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error clearing material: {e}")
            self.db.rollback()
            return False


class MaterialConceptRepository(MaterialRepositoryBase):
    def get_concept_id_map(self, material_id: int) -> dict[str, int]:
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

    def get_concept_pair_id_map(self, material_id: int) -> dict[tuple[str, str], int]:
        try:
            from models import Concept, Topic

            rows = (
                self.db.query(Concept.id, Concept.name, Topic.name)
                .join(Topic)
                .filter(Topic.study_material_id == material_id)
                .all()
            )
            concept_pair_map: dict[tuple[str, str], int] = {}
            for concept_id, concept_name, topic_name in rows:
                topic_key = (topic_name or "").strip().lower()
                concept_key = (concept_name or "").strip().lower()
                if not topic_key or not concept_key:
                    continue
                pair_key = (topic_key, concept_key)
                if pair_key not in concept_pair_map:
                    concept_pair_map[pair_key] = concept_id
            return concept_pair_map
        except Exception as e:
            print(f"Error loading concept pair map: {e}")
            return {}

    def get_concept_pairs(self, material_id: int) -> list[tuple[str, str]]:
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
