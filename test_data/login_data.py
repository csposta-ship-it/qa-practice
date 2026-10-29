INVALID_LOGIN_CASES = [
    ("student", "wrongpassword", "Your password is invalid!"),
    ("wronguser", "Password123", "Your username is invalid!"),
    ("", "Password123", "Your username is invalid!"),
]

SUCCESSFUL_LOGIN_CASES = [
    ("student", "Password123", "Logged In Successfully"),
]

dummy_user = {
    "username": "test_user",
    "email": "test@example.com",
    "password": "dummy_password",
    "type": "RETAIL"
}
