from app.helpers.api_helpers import password_match
from app.models.user import User
from app.operations.validator import Validator


class Login(Validator):
    def __init__(self, email=None, password=None):
        super().__init__()
        self.email = email
        self.password = password
        self.user = None
        self.payload = {"email": [], "password": []}

    def execute(self):
        if self.email:
            self.user = User.query.filter_by(email=self.email).first()

        if not self.email:
            self.payload["email"].append("email required")
        elif self.user is None:
            self.payload["email"].append("user not found")

        if not self.password:
            self.payload["password"].append("password required")

        if self.user is not None and self.password:
            if not password_match(self.password, self.user.password_hash):
                self.payload["password"].append("invalid password")
            elif self.user.status == "inactive":
                self.payload["email"].append("user inactive")

        self.count_errors()
