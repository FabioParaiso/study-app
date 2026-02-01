import pytest
from pydantic import ValidationError
from schemas.student import StudentCreate


@pytest.mark.parametrize(
    "password, expected_error",
    [
        ("Short1!", "at least 8 characters"),
        ("lowercase1!", "uppercase letter"),
        ("UPPERCASE1!", "lowercase letter"),
        ("NoNumber!", "one number"),
        ("NoSpecial1", "special character"),
    ],
)
def test_student_create_password_validation(password, expected_error):
    with pytest.raises(ValidationError) as exc:
        StudentCreate(name="TestUser", password=password)

    assert expected_error in str(exc.value)


def test_student_create_valid_password():
    student = StudentCreate(name="ValidUser", password="StrongPass1!")

    assert student.name == "ValidUser"
