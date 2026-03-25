from app.main import calculate, check_admin, hash_password


def test_calculate():
    assert calculate("1 + 1") == 2


def test_check_admin():
    assert check_admin("admin1234") is True
    assert check_admin("wrongpassword") is False


def test_hash_password():
    result = hash_password("password")
    assert isinstance(result, str)
    assert len(result) == 32
