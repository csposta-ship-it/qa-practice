class LoginPage:

    def __init__(self, page):
        self.page = page

    def open(self):
        self.page.goto(
            "https://practicetestautomation.com/practice-test-login/"
        )

    def login(self, username, password):
        self.page.get_by_label("Username").fill(username)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role(
            "button", name="Submit"
        ).click()

    def get_error_message(self):
        return self.page.locator("#error")

    def get_success_message(self):
        return self.page.get_by_text("Logged In Successfully")