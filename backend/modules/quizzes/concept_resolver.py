from modules.materials.ports import MaterialConceptIdRepositoryPort


class ConceptIdResolver:
    def __init__(self, material_repo: MaterialConceptIdRepositoryPort):
        self.material_repo = material_repo

    def apply(self, material_id: int | None, analytics_data: list[dict]) -> list[dict]:
        if not material_id:
            return analytics_data

        concept_map = self.material_repo.get_concept_id_map(material_id)
        concept_pair_map = self.material_repo.get_concept_pair_id_map(material_id)
        for item in analytics_data:
            if item.get("concept_id") is None:
                concept_name = item.get("topic")
                question_topic = item.get("question_topic")
                if not concept_name:
                    continue

                concept_key = concept_name.strip().lower()
                if not concept_key:
                    continue

                if question_topic:
                    topic_key = question_topic.strip().lower()
                    if topic_key:
                        concept_id = concept_pair_map.get((topic_key, concept_key))
                        if concept_id is not None:
                            item["concept_id"] = concept_id
                            continue

                item["concept_id"] = concept_map.get(concept_key)
        return analytics_data
