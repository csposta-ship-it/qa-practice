from app.database import init_db, get_connection

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