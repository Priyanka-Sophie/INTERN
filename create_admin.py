from getpass import getpass

from werkzeug.security import generate_password_hash

from database import create_database, get_db_connection


def create_admin():
    create_database()

    print("\nINTERN Admin Account Setup\n")

    full_name = input("Admin full name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ").strip()
    confirm_password = getpass("Confirm password: ").strip()

    if not full_name:
        print("Full name is required.")
        return

    if not email:
        print("Email is required.")
        return

    if "@" not in email or "." not in email:
        print("Enter a valid email address.")
        return

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    connection = get_db_connection()

    existing_admin = connection.execute(
        """
        SELECT id
        FROM admins
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    if existing_admin:
        connection.close()
        print("An admin account with this email already exists.")
        return

    password_hash = generate_password_hash(password)

    connection.execute(
        """
        INSERT INTO admins (
            full_name,
            email,
            password_hash,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            full_name,
            email,
            password_hash,
            "Active"
        )
    )

    connection.commit()
    connection.close()

    print("\nAdmin account created successfully.")


if __name__ == "__main__":
    create_admin()