import pytest
from pydantic import ValidationError

from app.schemas.auth import UserCreate


def test_user_create_accepts_bcrypt_safe_password() -> None:
    payload = UserCreate(email="reader@example.com", username="reader", password="password123")

    assert payload.email == "reader@example.com"
    assert payload.username == "reader"


def test_user_create_rejects_password_over_72_bytes() -> None:
    with pytest.raises(ValidationError) as exc:
        UserCreate(email="reader@example.com", username="reader", password="a" * 73)

    assert "72" in str(exc.value)


def test_user_create_rejects_multibyte_password_over_72_bytes() -> None:
    with pytest.raises(ValidationError) as exc:
        UserCreate(email="reader@example.com", username="reader", password="🙂" * 19)

    assert "72 bytes" in str(exc.value)
