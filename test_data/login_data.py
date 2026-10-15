INVALID_LOGIN_CASES = [
    ("student", "wrongpassword", "Your password is invalid!"),
    ("wronguser", "Password123", "Your username is invalid!"),
    ("", "Password123", "Your username is invalid!"),
]

SUCCESSFUL_LOGIN_CASES = [
    ("student", "Password123", "Logged In Successfully"),
]