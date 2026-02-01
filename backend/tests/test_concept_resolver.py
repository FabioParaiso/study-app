from modules.quizzes.concept_resolver import ConceptIdResolver


class DummyRepo:
    def get_concept_id_map(self, material_id: int):
        return {"cell": 42}


def test_concept_resolver_sets_concept_id():
    resolver = ConceptIdResolver(DummyRepo())
    analytics = [{"topic": "Cell", "concept_id": None, "is_correct": True}]

    resolved = resolver.apply(material_id=1, analytics_data=analytics)

    assert resolved[0]["concept_id"] == 42


def test_concept_resolver_no_material_id_returns_unchanged():
    resolver = ConceptIdResolver(DummyRepo())
    analytics = [{"topic": "Cell", "concept_id": None, "is_correct": True}]

    resolved = resolver.apply(material_id=None, analytics_data=analytics)

    assert resolved == analytics
