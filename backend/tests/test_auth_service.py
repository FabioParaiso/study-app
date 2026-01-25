import pytest
from repositories.student_repository import StudentAuthRepository
from services.auth_service import AuthService, AuthServiceError


class TestAuthService:
    @pytest.fixture
    def auth_service(self, db_session):
        repo = StudentAuthRepository(db_session)
        return AuthService(repo)

    def test_register_creates_student(self, auth_service):
        student = auth_service.register("NewUser", "StrongPass1!")

        assert student is not None
        assert student.name == "NewUser"
        assert student.hashed_password != "StrongPass1!"

    def test_register_duplicate_raises(self, auth_service):
        auth_service.register("DupeUser", "StrongPass1!")

        with pytest.raises(AuthServiceError) as exc:
            auth_service.register("DupeUser", "AnotherPass1!")

        assert exc.value.status_code == 400

    def test_login_success(self, auth_service):
        auth_service.register("AuthUser", "ValidPass1!")

        student = auth_service.login("AuthUser", "ValidPass1!")

        assert student is not None
        assert student.name == "AuthUser"

    def test_login_wrong_password_raises(self, auth_service):
        auth_service.register("AuthUser2", "ValidPass1!")

        with pytest.raises(AuthServiceError) as exc:
            auth_service.login("AuthUser2", "WrongPass1!")

        assert exc.value.status_code == 401

    def test_login_missing_user_raises(self, auth_service):
        with pytest.raises(AuthServiceError) as exc:
            auth_service.login("Ghost", "AnyPass1!")

        assert exc.value.status_code == 401
