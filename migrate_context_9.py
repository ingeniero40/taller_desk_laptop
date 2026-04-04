import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def migrate():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL no encontrada.")
        return

    engine = create_engine(db_url)
    
    commands = [
        "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS entry_images TEXT;",
        "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS exit_images TEXT;",
        "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS client_signature TEXT;",
        "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS is_delivered BOOLEAN DEFAULT FALSE;"
    ]

    with engine.connect() as conn:
        for cmd in commands:
            print(f"Ejecutando: {cmd}")
            conn.execute(text(cmd))
            conn.commit()
    print("✅ Migración del Contexto 9 exitosa.")

if __name__ == "__main__":
    migrate()
