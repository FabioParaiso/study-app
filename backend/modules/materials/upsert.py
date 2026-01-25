from datetime import datetime
from models import StudyMaterial, Topic, Concept
from services.ports import MaterialUpsertRepositoryPort


class MaterialUpserter:
    def __init__(self, repo: MaterialUpsertRepositoryPort):
        self.repo = repo

    def upsert(self, student_id: int, text: str, source_name: str, topics: dict[str, list[str]] | None):
        if not self.repo.deactivate_all(student_id, commit=False):
            return None

        material = self.repo.find_by_source(student_id, source_name)
        if material:
            material.text = text
            material.is_active = True
            material.last_accessed = datetime.utcnow()
        else:
            material = StudyMaterial(
                student_id=student_id,
                text=text,
                source=source_name,
                is_active=True,
                last_accessed=datetime.utcnow()
            )

        material.topics = self._build_topics(topics)
        return self.repo.save_material(material)

    @staticmethod
    def _build_topics(topics: dict[str, list[str]] | None) -> list[Topic]:
        if not topics:
            return []

        new_topic_objs = []
        for topic_name, concepts_list in topics.items():
            topic_obj = Topic(name=topic_name)
            topic_obj.concepts = [Concept(name=c_name) for c_name in concepts_list]
            new_topic_objs.append(topic_obj)
        return new_topic_objs
