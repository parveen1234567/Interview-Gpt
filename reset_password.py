import getpass
import sys

from config.database import SessionLocal
from models.user import User
from services.auth import hash_password, verify_password


MIN_PASSWORD_LENGTH = 12
MAX_BCRYPT_BYTES = 72


def main():
    if len(sys.argv) != 2:
        print("Usage: python reset_password.py <account-email>", file=sys.stderr)
        return 2

    email = sys.argv[1].strip()
    if not email:
        print("An account email is required.", file=sys.stderr)
        return 2

    password = getpass.getpass("New password (input hidden): ")
    confirmation = getpass.getpass("Confirm new password: ")

    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        return 2
    if len(password) < MIN_PASSWORD_LENGTH:
        print(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters.",
            file=sys.stderr,
        )
        return 2
    if len(password.encode("utf-8")) > MAX_BCRYPT_BYTES:
        print(
            f"Password must be no more than {MAX_BCRYPT_BYTES} UTF-8 bytes.",
            file=sys.stderr,
        )
        return 2

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one_or_none()
        if user is None:
            print(f"No account found for {email}.", file=sys.stderr)
            return 1

        user.password = hash_password(password)
        db.commit()
        db.refresh(user)
        if not verify_password(password, user.password):
            raise RuntimeError(
                "The saved password hash could not be verified. Check the app's database configuration."
            )
        print(f"Password updated for {email}.")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
