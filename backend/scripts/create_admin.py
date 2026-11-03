
import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.user import User, UserRole


def main():
    username = input("Admin username: ").strip()

    if len(username) < 3:
        print("Username must contain at least 3 characters.")
        return

    password = getpass.getpass("Admin password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if len(password) < 12:
        print("Use at least 12 characters for the admin password.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(User.username == username)
        )

        if existing_user:
            print("Username already exists.")
            return

        admin = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print(f"Administrator '{username}' created successfully.")


if __name__ == "__main__":
    main()
