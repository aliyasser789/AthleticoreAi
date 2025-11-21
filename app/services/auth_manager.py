from app.models.user import User
from app.db import db_helper
from app.services.email_service import send_email  # NEW
import hashlib
import secrets                                     # NEW
import string                                      


class Authentication_manager:
    @staticmethod
    def hash_password(real_password):
        password_bytes = real_password.encode("utf-8")
        hash_password_obj = hashlib.sha256(password_bytes)
        hash_password_string = hash_password_obj.hexdigest()
        return hash_password_string

    @staticmethod
    def _generate_temp_password(length: int = 12) -> str:
        """Generate a random temporary password."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def register_user(username, email, password, age, gender, height, weight):
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if row is not None:
            print("Username already taken")
            return None

        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        if row is not None:
            print("Email already taken")
            return None

        hashed_pass = Authentication_manager.hash_password(password)
        created_at = User.now_iso()

        db_helper.execute_query(
            "INSERT INTO users (username, email, password_hash, created_at, age, gender, height, weight) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, email, hashed_pass, created_at, age, gender, height , weight)
        )

        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        new_user = User.from_row(row)
        return new_user

    @staticmethod
    def login_user(username_or_email, password):
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email)
        )
        if row is None:
            print("User not found (wrong username or email).")
            return None

        user = User.from_row(row)
        entered_hash = Authentication_manager.hash_password(password)

        if entered_hash != user.password_hash:
            print("WRONG PASSWORD")
            return None

        return user

    @staticmethod
    def forget_password(email):
        # 1) Look up user by email in the database
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        if row is None:
            print("No user found with this email.")
            return None

        # Same as before: build User from row (we need user.id)
        user = User.from_row(row)

        # 2) Generate a secure random temporary password
        temp_pass = Authentication_manager._generate_temp_password(length=12)

        # 3) Hash the temporary password using your existing function
        temp_pass_hash = Authentication_manager.hash_password(temp_pass)

        # 4) Update password_hash in DB
        db_helper.execute_query(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (temp_pass_hash, user.id)
        )

        # 5) Send the temporary password by email
        subject = "Your Athleticore.AI Temporary Password"
        body = (
            "Hello,\n\n"
            "You requested a password reset for your Athleticore.AI account.\n\n"
            f"Your temporary password is:\n\n"
            f"    {temp_pass}\n\n"
            "Please use this temporary password to log in, and then change your password "
            "from the settings screen.\n\n"
            "If you did not request this, please ignore this email.\n"
        )

        # Use the email string passed into the function (no dependency on user.email)
        email_sent = send_email(email, subject, body)

        if not email_sent:
            print("Failed to send temporary password email to", email)

        return user
