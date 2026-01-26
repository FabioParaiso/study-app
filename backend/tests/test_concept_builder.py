from modules.quizzes.policies import ConceptWhitelistBuilder

def test_concept_whitelist_builder_deduplication_all_topics():
    """
    Verifies that ConceptWhitelistBuilder.build deduplicates concepts
    when no target topics are provided (all topics case), preserving the first casing.
    """
    material_topics_data = {
        "Topic A": ["Concept 1", "concept 2", "Duplicate"],
        "Topic B": ["Concept 2", "DUPLICATE", "Concept 3"]
    }

    # Act: Build concept list without target topics (should get all unique concepts)
    concepts = ConceptWhitelistBuilder.build(material_topics_data, target_topics=None)

    # Assert
    assert len(concepts) == 4, f"Expected 4 unique concepts, got {len(concepts)}: {concepts}"

    # Verify exact casing based on first occurrence
    expected_concepts = {"Concept 1", "concept 2", "Duplicate", "Concept 3"}
    assert set(concepts) == expected_concepts

    # Verify no case-insensitive duplicates remain
    lower_concepts = [c.lower() for c in concepts]
    assert len(lower_concepts) == len(set(lower_concepts)), "Case-insensitive duplicates found"

def test_concept_whitelist_builder_target_topics_consistency():
    """
    Verifies that the existing logic for target topics also handles duplicates correctly.
    (This ensures we didn't break or misunderstand the existing logic)
    """
    material_topics_data = {
        "topic a": ["Concept 1", "Concept 1"],  # Duplicate inside same topic
        "topic b": ["Concept 2"]
    }

    concepts = ConceptWhitelistBuilder.build(material_topics_data, target_topics=["Topic A"])

    assert len(concepts) == 1
    assert concepts[0] == "Concept 1"
