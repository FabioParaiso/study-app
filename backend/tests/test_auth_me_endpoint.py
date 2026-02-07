from models import Student


def test_me_endpoint_returns_challenge_xp(client, db_session):
    register = client.post("/register", json={"name": "MeEndpointUser", "password": "StrongPass1!"})
    assert register.status_code == 200

    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    student = db_session.query(Student).filter(Student.name == "MeEndpointUser").first()
    student.challenge_xp = 123
    db_session.commit()

    response = client.get("/me", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "MeEndpointUser"
    assert data["challenge_xp"] == 123
    assert "total_xp" in data
    assert "high_score" in data
