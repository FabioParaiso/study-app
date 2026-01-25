import pytest
from repositories.student_repository import StudentRepository
from models import Student
from security import get_password_hash

class TestStudentRepository:
    
    @pytest.fixture
    def repo(self, db_session):
        """Fixture provides repo with test DB session (tables created by autouse init_db)."""
        yield StudentRepository(db_session)


    def test_create_student_new_user(self, repo):
        """Test creating a completely new student."""
        hashed_password = get_password_hash("StrongPass1!")
        student = repo.create_student("NewUser", hashed_password)
        
        assert student is not None
        assert student.name == "NewUser"
        assert student.hashed_password is not None
        assert student.total_xp == 0
        assert student.high_score == 0

    def test_create_student_duplicate_returns_none(self, repo):
        """Test that duplicate registration returns None."""
        repo.create_student("DupeUser", get_password_hash("StrongPass1!"))
        duplicate = repo.create_student("DupeUser", get_password_hash("AnotherPass1!"))
        
        assert duplicate is None



    def test_get_by_name_returns_student(self, repo):
        """Test loading by name."""
        repo.create_student("AuthUser", get_password_hash("ValidPass1!"))
        loaded = repo.get_by_name("AuthUser")
        
        assert loaded is not None
        assert loaded.name == "AuthUser"

    def test_get_by_name_returns_none_for_missing(self, repo):
        """Test loading by name for non-existent user."""
        loaded = repo.get_by_name("Ghost")
        
        assert loaded is None



    def test_update_xp(self, repo):
        """Test XP update increments correctly."""
        student = repo.create_student("XPUser", get_password_hash("Pass1!"))
        original_id = student.id
        
        updated = repo.update_xp(original_id, 100)
        
        assert updated.total_xp == 100
        
        updated = repo.update_xp(original_id, 50)
        assert updated.total_xp == 150

    def test_update_avatar(self, repo):
        """Test avatar update."""
        student = repo.create_student("AvatarUser", get_password_hash("Pass1!"))
        
        updated = repo.update_avatar(student.id, "🚀")
        
        assert updated.current_avatar == "🚀"

    def test_update_high_score_increases(self, repo):
        """Test high score updates when new score is higher."""
        student = repo.create_student("ScoreUser", get_password_hash("Pass1!"))
        
        updated = repo.update_high_score(student.id, 100)
        assert updated.high_score == 100
        
        updated = repo.update_high_score(student.id, 150)
        assert updated.high_score == 150

    def test_update_high_score_does_not_decrease(self, repo):
        """Test high score does not decrease if new score is lower."""
        student = repo.create_student("ScoreUser2", get_password_hash("Pass1!"))
        repo.update_high_score(student.id, 200)
        
        updated = repo.update_high_score(student.id, 100)
        
        assert updated.high_score == 200
