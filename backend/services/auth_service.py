from security import get_password_hash, verify_password
from services.ports import StudentAuthRepositoryPort


class AuthServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class AuthService:
    def __init__(self, repo: StudentAuthRepositoryPort):
        self.repo = repo

    def register(self, name: str, password: str):
        hashed_password = get_password_hash(password)
        student = self.repo.create_student(name, hashed_password)
        if not student:
            raise AuthServiceError("Esse nome já existe. Tenta fazer Login ou escolhe outro nome.", status_code=400)
        return student

    def login(self, name: str, password: str):
        student = self.repo.get_by_name(name)
        if not student or not verify_password(password, student.hashed_password):
            raise AuthServiceError("Credenciais inválidas. Verifica o nome e a password.", status_code=401)
        return student
