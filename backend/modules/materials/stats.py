from services.ports import MaterialRepositoryPort


class MaterialStatsUpdater:
    def __init__(self, repo: MaterialRepositoryPort):
        self.repo = repo

    def apply(self, material_id: int, score: int, total_questions: int, xp_earned: int) -> bool:
        stats = self.repo.get_stats_by_id(material_id)
        if not stats:
            return False

        total_questions_answered = stats["total_questions_answered"] + total_questions
        correct_answers_count = stats["correct_answers_count"] + score
        total_xp = stats["total_xp"] + xp_earned
        high_score = max(stats["high_score"], score)

        return self.repo.set_stats(
            material_id=material_id,
            total_questions_answered=total_questions_answered,
            correct_answers_count=correct_answers_count,
            total_xp=total_xp,
            high_score=high_score
        )
