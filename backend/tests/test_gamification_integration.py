import pytest

def test_xp_and_avatar_update_flow(client):
    """Integration test: Register → Update Avatar → Add XP."""
    
    # 1. Register user
    register_response = client.post("/register", json={"name": "GameUserInt", "password": "StrongPass1!"})
    assert register_response.status_code == 200
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Update Avatar
    avatar_update = {"avatar": "🚀"}
    avatar_response = client.post("/gamification/avatar", json=avatar_update, headers=headers)
    assert avatar_response.status_code == 200
    assert avatar_response.json()["current_avatar"] == "🚀"
    
    # 3. Get student info to verify avatar persisted
    login_response = client.post("/login", json={"name": "GameUserInt", "password": "StrongPass1!"})
    user = login_response.json()["user"]
    assert user["current_avatar"] == "🚀"
    assert user["total_xp"] == 0
    
    # 4. Add XP
    xp_update = {"amount": 100}
    xp_response = client.post("/gamification/xp", json=xp_update, headers=headers)
    assert xp_response.status_code == 200
    assert xp_response.json()["total_xp"] == 100
    
    # 5. Update high score
    score_update = {"score": 85}
    score_response = client.post("/gamification/highscore", json=score_update, headers=headers)
    assert score_response.status_code == 200
    assert score_response.json()["high_score"] == 85
    
    # 6. Try to update with lower score (should not decrease)
    score_update_low = {"score": 50}
    client.post("/gamification/highscore", json=score_update_low, headers=headers)
    
    login_response = client.post("/login", json={"name": "GameUserInt", "password": "StrongPass1!"})
    user = login_response.json()["user"]
    assert user["high_score"] == 85  # Unchanged


def test_multiple_xp_updates_accumulate(client):
    """Integration test: Multiple XP updates should accumulate correctly."""
    
    register_response = client.post("/register", json={"name": "XPUserInt", "password": "StrongPass1!"})
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add XP multiple times
    client.post("/gamification/xp", json={"amount": 50}, headers=headers)
    client.post("/gamification/xp", json={"amount": 75}, headers=headers)
    client.post("/gamification/xp", json={"amount": 25}, headers=headers)
    
    # Verify total via login
    login_response = client.post("/login", json={"name": "XPUserInt", "password": "StrongPass1!"})
    user = login_response.json()["user"]
    assert user["total_xp"] == 150


def test_avatar_persistence_across_sessions(client):
    """Integration test: Avatar should persist after logout/login."""
    
    # Register and set avatar
    register_response = client.post("/register", json={"name": "PersistAvatarInt", "password": "StrongPass1!"})
    token1 = register_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    client.post("/gamification/avatar", json={"avatar": "🎯"}, headers=headers1)
    
    # "Logout" and login again (get new token)
    login_response = client.post("/login", json={"name": "PersistAvatarInt", "password": "StrongPass1!"})
    user = login_response.json()["user"]
    
    # Verify avatar persisted
    assert user["current_avatar"] == "🎯"
