import sqlite3
from contextlib import closing
from pathlib import Path

from pwdlib import PasswordHash


DATABASE_PATH = (
    Path.home()
    / "OneDrive"
    / "Desktop"
    / "qa_practice_data"
    / "qa_practice.db"
)

USER_MIGRATIONS = {
    'customer_id': "TEXT",
    'type': "TEXT NOT NULL DEFAULT 'RETAIL'",
    'company_name': "TEXT",
}

password_hash = PasswordHash.recommended()


def get_connection(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path=DATABASE_PATH):
    with closing(get_connection(db_path)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
            """)
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(users)")
            }
            for name, value in USER_MIGRATIONS.items():
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE users ADD COLUMN {name} {value}"
                    )
            connection.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            audit_columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(audit_logs)"
                )
            }
            for column in ("request_id", "request_data", "response_data"):
                if column not in audit_columns:
                    connection.execute(
                        f"ALTER TABLE audit_logs ADD COLUMN {column} TEXT"
                    )

            connection.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_users_customer_id
                ON users(customer_id)
            """)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def create_user(
    username: str,
    email: str,
    password: str,
    user_type: str,
    company_name: str | None = None,
):
    hashed_password = hash_password(password)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (username, email, password_hash, type, company_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, email, hashed_password, user_type, company_name),
        )

        user_id = cursor.lastrowid
        customer_id = f"CUST-{user_id:06d}"

        connection.execute(
            "UPDATE users SET customer_id = ? WHERE id = ?",
            (customer_id, user_id),
        )

        return {
            "id": user_id,
            "customer_id": customer_id,
        }


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def write_audit_log(
    event_type: str,
    user_id: int | None = None,
    details: str | None = None,
    request_id: str | None = None,
    request_data: str | None = None,
    response_data: str | None = None,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO audit_logs (
                user_id,
                event_type,
                details,
                request_id,
                request_data,
                response_data
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                event_type,
                details,
                request_id,
                request_data,
                response_data,
            ),
        )
