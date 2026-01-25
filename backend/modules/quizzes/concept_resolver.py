from services.ports import MaterialConceptIdRepositoryPort


class ConceptIdResolver:
    def __init__(self, material_repo: MaterialConceptIdRepositoryPort):
        self.material_repo = material_repo

    def apply(self, material_id: int | None, analytics_data: list[dict]) -> list[dict]:
        if not material_id:
            return analytics_data

        concept_map = self.material_repo.get_concept_id_map(material_id)
        for item in analytics_data:
            if item.get("concept_id") is None:
                concept_name = item.get("topic")
                if concept_name:
                    item["concept_id"] = concept_map.get(concept_name.strip().lower())
        return analytics_data
