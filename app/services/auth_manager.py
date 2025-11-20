from app.models.user import User
from app.db import db_helper
import hashlib


class Authentication_manager:
    @staticmethod
    def hash_passowrd(real_password):
        password_bytes = real_password.encode("utf-8")
        hash_password_obj = hashlib.sha256(password_bytes)
        hash_password_string = hash_password_obj.hexdigest()
        return hash_password_string

    @staticmethod
    def register_user(username, email, password):
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

        hashed_pass = Authentication_manager.hash_passowrd(password)
        created_at = User.now_iso()

        db_helper.execute_query(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, hashed_pass, created_at)
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
        entered_hash = Authentication_manager.hash_passowrd(password)

        if entered_hash != user.password_hash:
            print("WRONG PASSWORD")
            return None

        return user

    @staticmethod
    def forget_password(email):
        row = db_helper.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        if row is None:
            print("No user found with this email.")
            return None

        user = User.from_row(row)
        temp_pass = "temppass1234_change by email sending later"
        temp_pass_hash = Authentication_manager.hash_passowrd(temp_pass)

        db_helper.execute_query(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (temp_pass_hash, user.id)
        )

        print("Temporary password for user", user.email, "is:", temp_pass)
        return user




