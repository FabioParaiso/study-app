from models import QuizResult
from dependencies import get_challenge_service


class _FailingChallengeService:
    def process_session(self, **kwargs):
        raise RuntimeError("boom")

    def get_weekly_status(self, student_id: int):
        return {}


def test_quiz_result_persists_even_if_challenge_hook_fails(client, db_session, auth_headers):
    client.app.dependency_overrides[get_challenge_service] = lambda: _FailingChallengeService()

    try:
        payload = {
            "score": 4,
            "total_questions": 5,
            "quiz_type": "multiple-choice",
            "detailed_results": [
                {"topic": "Biologia", "is_correct": True},
                {"topic": "Biologia", "is_correct": True},
                {"topic": "Biologia", "is_correct": False},
                {"topic": "Biologia", "is_correct": True},
                {"topic": "Biologia", "is_correct": True},
            ],
            "active_seconds": 240,
            "duration_seconds": 260,
        }

        response = client.post("/quiz/result", json=payload, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "saved"

        persisted = db_session.query(QuizResult).all()
        assert len(persisted) == 1
    finally:
        client.app.dependency_overrides.pop(get_challenge_service, None)
