from models import StudyMaterial


class MaterialMapper:
    @staticmethod
    def topics_map(material: StudyMaterial) -> dict[str, list[str]]:
        topics_dict: dict[str, list[str]] = {}
        if not material or not material.topics:
            return topics_dict

        for topic in material.topics:
            topics_dict[topic.name] = [c.name for c in topic.concepts]
        return topics_dict

    @staticmethod
    def to_dict(material: StudyMaterial) -> dict:
        topics_dict = MaterialMapper.topics_map(material)
        return {
            "id": material.id,
            "text": material.text,
            "source": material.source,
            "topics": topics_dict,
            "total_xp": material.total_xp,
            "high_score": material.high_score,
            "total_questions_answered": material.total_questions_answered,
            "correct_answers_count": material.correct_answers_count,
        }

    @staticmethod
    def to_list_item(material: StudyMaterial) -> dict:
        return {
            "id": material.id,
            "source": material.source,
            "created_at": material.created_at,
            "is_active": material.is_active,
            "preview": material.text[:100] if material.text else "",
            "total_xp": material.total_xp,
        }
