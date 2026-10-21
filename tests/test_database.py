from app.database import init_db, get_connection
import allure

@allure.title("Database initialization creates required tables")
@allure.description(
    "Verify that initialization creates the required tables "
    "and audit log columns."
)

def test_init_db_creates_tables(tmp_path):
    
    db_path = tmp_path / "test_db.db"
    init_db(db_path)

    with get_connection(db_path) as connection:
        table_cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )

        column_cursor = connection.execute(
            "PRAGMA table_info(audit_logs)"
        )

        rows = table_cursor.fetchall()

        table_names = {row[0] for row in rows}

        columns = column_cursor.fetchall()

        column_names = {row[1] for row in columns}

        assert "users" in table_names
        assert "audit_logs" in table_names
        assert "request_id" in column_names
        assert "request_data" in column_names
        assert "response_data" in column_names

@allure.title("Database initialization migrates legacy users table")
@allure.description(
    "Verify that initialization adds the required columns "
    "to an existing legacy users table."
)

def test_init_db_migrates_users_table(tmp_path):

    db_path = tmp_path / "legacy.db"
    with get_connection(db_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        connection.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES ('legacy_user', 'legacy@example.com', 'dummy_hash');
        """)

    init_db(db_path)

    with get_connection(db_path) as connection: 
        
        user_columns = connection.execute(
            "PRAGMA table_info(users)"
        )

        legacy_user = connection.execute("""
            SELECT type, customer_id, company_name
            FROM users
            WHERE username = 'legacy_user';
        """)
        
        columns = user_columns.fetchall()
        
        column_names = {row[1] for row in columns}

        legacy_data = legacy_user.fetchone()

        assert legacy_data["type"] == "RETAIL"
        assert legacy_data["customer_id"] == None
        assert legacy_data["company_name"] == None
        assert "customer_id" in column_names
        assert "type" in column_names
        assert "company_name" in column_names

@allure.title("Database initialization migrates legacy audit_logs")
@allure.description(
    "Verify that initialization adds the required columns "
    "to an existing legacy audit_logs."
)

def test_init_db_migrates_audit_logs(tmp_path):

    db_path= tmp_path / "legacy.db"
    with get_connection(db_path) as connection:
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

    init_db(db_path)

    with get_connection(db_path) as connection: 
        
        audit_columns = connection.execute(
            "PRAGMA table_info(audit_logs)"
        )
                
        columns = audit_columns.fetchall()
        
        column_names = {row[1] for row in columns}

        assert "request_id" in column_names
        assert "request_data" in column_names
        assert "response_data" in column_names


@allure.title("Database initialization can run multiple times")
@allure.description(
    "Verify that repeated initialization preserves the required "
    "tables and columns in users and audit_logs."
)

def test_init_db_can_run_multiple_times(tmp_path):

    db_path = tmp_path / "test_db.db"
    init_db(db_path)
    init_db(db_path)

    with get_connection(db_path) as connection:
            table_cursor = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
    
            column_cursor = connection.execute(
                "PRAGMA table_info(audit_logs)"
            )
    
            rows = table_cursor.fetchall()
    
            table_names = {row[0] for row in rows}
    
            columns = column_cursor.fetchall()
    
            column_names = {row[1] for row in columns}
    
            assert "audit_logs" in table_names
            assert "request_id" in column_names
            assert "request_data" in column_names
            assert "response_data" in column_names

            cursor = connection.execute(
                 "PRAGMA table_info(users)"
            )

            table_names = {row[0] for row in rows}

            columns = cursor.fetchall()

            column_names = {row[1] for row in columns}

            assert "users" in table_names
            assert "id" in column_names
            assert "username" in column_names
            assert "email" in column_names
            assert "password_hash" in column_names
            assert "customer_id" in column_names
            assert "type" in column_names
            assert "company_name" in column_names
            