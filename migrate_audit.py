import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def migrate_audit():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL no encontrada.")
        return

    engine = create_engine(db_url)
    
    commands = [
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id UUID PRIMARY KEY,
            user_id UUID,
            user_name TEXT,
            action TEXT NOT NULL,
            module TEXT NOT NULL,
            entity_id TEXT,
            entity_type TEXT,
            previous_value TEXT,
            new_value TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_id);",
        "CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_logs(entity_type);",
        "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);"
    ]

    with engine.connect() as conn:
        for cmd in commands:
            print(f"Ejecutando: {cmd[:50]}...")
            conn.execute(text(cmd))
            conn.commit()
    print("✅ Migración de Auditoría exitosa.")

if __name__ == "__main__":
    migrate_audit()
