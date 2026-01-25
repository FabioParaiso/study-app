from services.ports import StudentRepositoryPort


class AuthServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class AuthService:
    def __init__(self, repo: StudentRepositoryPort):
        self.repo = repo

    def register(self, name: str, password: str):
        student = self.repo.create_student(name, password)
        if not student:
            raise AuthServiceError("Esse nome já existe. Tenta fazer Login ou escolhe outro nome.", status_code=400)
        return student

    def login(self, name: str, password: str):
        student = self.repo.authenticate_student(name, password)
        if not student:
            raise AuthServiceError("Credenciais inválidas. Verifica o nome e a password.", status_code=401)
        return student
