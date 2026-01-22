import pytest
from repositories.student_repository import StudentRepository
from models import Student

class TestStudentRepository:
    
    @pytest.fixture
    def repo(self, db_session):
        """Fixture provides repo with test DB session (tables created by autouse init_db)."""
        yield StudentRepository(db_session)


    def test_create_student_new_user(self, repo):
        """Test creating a completely new student."""
        student = repo.create_student("NewUser", "StrongPass1!")
        
        assert student is not None
        assert student.name == "NewUser"
        assert student.hashed_password is not None
        assert student.total_xp == 0
        assert student.high_score == 0

    def test_create_student_duplicate_returns_none(self, repo):
        """Test that duplicate registration returns None."""
        repo.create_student("DupeUser", "StrongPass1!")
        duplicate = repo.create_student("DupeUser", "AnotherPass1!")
        
        assert duplicate is None



    def test_authenticate_valid_credentials(self, repo):
        """Test authentication with correct password."""
        repo.create_student("AuthUser", "ValidPass1!")
        
        authenticated = repo.authenticate_student("AuthUser", "ValidPass1!")
        
        assert authenticated is not None
        assert authenticated.name == "AuthUser"

    def test_authenticate_wrong_password(self, repo):
        """Test authentication fails with wrong password."""
        repo.create_student("AuthUser2", "ValidPass1!")
        
        authenticated = repo.authenticate_student("AuthUser2", "WrongPass1!")
        
        assert authenticated is None

    def test_authenticate_nonexistent_user(self, repo):
        """Test authentication fails for non-existent user."""
        authenticated = repo.authenticate_student("Ghost", "AnyPass1!")
        
        assert authenticated is None



    def test_update_xp(self, repo):
        """Test XP update increments correctly."""
        student = repo.create_student("XPUser", "Pass1!")
        original_id = student.id
        
        updated = repo.update_xp(original_id, 100)
        
        assert updated.total_xp == 100
        
        updated = repo.update_xp(original_id, 50)
        assert updated.total_xp == 150

    def test_update_avatar(self, repo):
        """Test avatar update."""
        student = repo.create_student("AvatarUser", "Pass1!")
        
        updated = repo.update_avatar(student.id, "🚀")
        
        assert updated.current_avatar == "🚀"

    def test_update_high_score_increases(self, repo):
        """Test high score updates when new score is higher."""
        student = repo.create_student("ScoreUser", "Pass1!")
        
        updated = repo.update_high_score(student.id, 100)
        assert updated.high_score == 100
        
        updated = repo.update_high_score(student.id, 150)
        assert updated.high_score == 150

    def test_update_high_score_does_not_decrease(self, repo):
        """Test high score does not decrease if new score is lower."""
        student = repo.create_student("ScoreUser2", "Pass1!")
        repo.update_high_score(student.id, 200)
        
        updated = repo.update_high_score(student.id, 100)
        
        assert updated.high_score == 200
