import pytest
from repositories.student_repository import (
    StudentAuthRepository,
    StudentGamificationRepository,
    StudentLookupRepository,
    StudentXpRepository,
)
from security import get_password_hash

class TestStudentRepository:
    
    @pytest.fixture
    def auth_repo(self, db_session):
        """Fixture provides auth repo with test DB session (tables created by autouse init_db)."""
        yield StudentAuthRepository(db_session)

    @pytest.fixture
    def lookup_repo(self, db_session):
        yield StudentLookupRepository(db_session)

    @pytest.fixture
    def xp_repo(self, db_session):
        yield StudentXpRepository(db_session)

    @pytest.fixture
    def gamification_repo(self, db_session):
        yield StudentGamificationRepository(db_session)


    def test_create_student_new_user(self, auth_repo):
        """Test creating a completely new student."""
        hashed_password = get_password_hash("StrongPass1!")
        student = auth_repo.create_student("NewUser", hashed_password)
        
        assert student is not None
        assert student.name == "NewUser"
        assert student.hashed_password is not None
        assert student.total_xp == 0
        assert student.high_score == 0

    def test_create_student_duplicate_returns_none(self, auth_repo):
        """Test that duplicate registration returns None."""
        auth_repo.create_student("DupeUser", get_password_hash("StrongPass1!"))
        duplicate = auth_repo.create_student("DupeUser", get_password_hash("AnotherPass1!"))
        
        assert duplicate is None


    def test_get_by_name_returns_student(self, auth_repo):
        """Test loading by name."""
        auth_repo.create_student("AuthUser", get_password_hash("ValidPass1!"))
        loaded = auth_repo.get_by_name("AuthUser")
        
        assert loaded is not None
        assert loaded.name == "AuthUser"

    def test_get_by_name_returns_none_for_missing(self, auth_repo):
        """Test loading by name for non-existent user."""
        loaded = auth_repo.get_by_name("Ghost")
        
        assert loaded is None


    def test_get_student_by_id(self, auth_repo, lookup_repo):
        student = auth_repo.create_student("LookupUser", get_password_hash("StrongPass1!"))
        loaded = lookup_repo.get_student(student.id)

        assert loaded is not None
        assert loaded.id == student.id

    def test_update_xp(self, auth_repo, xp_repo):
        """Test XP update increments correctly."""
        student = auth_repo.create_student("XPUser", get_password_hash("Pass1!"))
        original_id = student.id
        
        updated = xp_repo.update_xp(original_id, 100)
        
        assert updated.total_xp == 100
        
        updated = xp_repo.update_xp(original_id, 50)
        assert updated.total_xp == 150

    def test_update_avatar(self, auth_repo, gamification_repo):
        """Test avatar update."""
        student = auth_repo.create_student("AvatarUser", get_password_hash("Pass1!"))
        
        updated = gamification_repo.update_avatar(student.id, "🚀")
        
        assert updated.current_avatar == "🚀"

    def test_update_high_score_increases(self, auth_repo, gamification_repo):
        """Test high score updates when new score is higher."""
        student = auth_repo.create_student("ScoreUser", get_password_hash("Pass1!"))
        
        updated = gamification_repo.update_high_score(student.id, 100)
        assert updated.high_score == 100
        
        updated = gamification_repo.update_high_score(student.id, 150)
        assert updated.high_score == 150

    def test_update_high_score_does_not_decrease(self, auth_repo, gamification_repo):
        """Test high score does not decrease if new score is lower."""
        student = auth_repo.create_student("ScoreUser2", get_password_hash("Pass1!"))
        gamification_repo.update_high_score(student.id, 200)
        
        updated = gamification_repo.update_high_score(student.id, 100)
        
        assert updated.high_score == 200
