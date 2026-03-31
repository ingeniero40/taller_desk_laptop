"""
migrate_admission.py
────────────────────
Migración segura para agregar los campos de Admisión de Equipos.

Aplica ALTER TABLE ... ADD COLUMN IF NOT EXISTS, lo que garantiza:
- Idempotencia: ejecutar múltiples veces no produce errores.
- Seguridad de datos: no toca filas existentes.
- Compatibilidad retroactiva: los valores nuevos son NULL o tienen DEFAULT.

Entidades afectadas:
  - devices   → physical_condition, accessories, photo_url, device_type
  - work_orders → priority, due_date

Uso:
    python migrate_admission.py
"""

import os
import sys
from dotenv import load_dotenv

# ── Path Setup ──────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PGMESSAGELANG", "English")

load_dotenv()

# ── Migraciones ────────────────────────────────────────────────────────────

MIGRATIONS = [
    # ── Tabla devices ──────────────────────────────────────────────────────
    {
        "description": "devices → device_type VARCHAR(50)",
        "sql": """
            ALTER TABLE devices
            ADD COLUMN IF NOT EXISTS device_type VARCHAR(50) DEFAULT 'Laptop/PC';
        """
    },
    {
        "description": "devices → physical_condition TEXT",
        "sql": """
            ALTER TABLE devices
            ADD COLUMN IF NOT EXISTS physical_condition TEXT;
        """
    },
    {
        "description": "devices → accessories TEXT",
        "sql": """
            ALTER TABLE devices
            ADD COLUMN IF NOT EXISTS accessories TEXT;
        """
    },
    {
        "description": "devices → photo_url TEXT",
        "sql": """
            ALTER TABLE devices
            ADD COLUMN IF NOT EXISTS photo_url TEXT;
        """
    },

    # ── Tabla work_orders ──────────────────────────────────────────────────
    {
        "description": "work_orders → priority VARCHAR(20)",
        "sql": """
            ALTER TABLE work_orders
            ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'Media';
        """
    },
    {
        "description": "work_orders → due_date TIMESTAMP",
        "sql": """
            ALTER TABLE work_orders
            ADD COLUMN IF NOT EXISTS due_date TIMESTAMP;
        """
    },
]


def run_migrations():
    import psycopg2

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌  ERROR: DATABASE_URL no encontrada en .env")
        sys.exit(1)

    print("\n🗄️  Gravity — Migration: Admission Module")
    print("─" * 44)

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        cursor = conn.cursor()

        ok_count = 0
        for migration in MIGRATIONS:
            try:
                print(f"  ▶  {migration['description']} ...", end=" ")
                cursor.execute(migration["sql"])
                print("✅")
                ok_count += 1
            except Exception as e:
                print(f"❌  FAILED: {e}")
                conn.rollback()
                cursor.close()
                conn.close()
                sys.exit(1)

        conn.commit()
        cursor.close()
        conn.close()

        print("─" * 44)
        print(f"✅  Migración completada: {ok_count}/{len(MIGRATIONS)} operaciones aplicadas.")
        print("   Las columnas existentes no fueron modificadas (IF NOT EXISTS).")
        print("─" * 44)

    except psycopg2.OperationalError as e:
        print(f"\n❌  No se pudo conectar a PostgreSQL: {e}")
        sys.exit(1)


def verify_columns():
    """Verifica que las columnas existan tras la migración."""
    import psycopg2

    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    checks = [
        ("devices", "device_type"),
        ("devices", "physical_condition"),
        ("devices", "accessories"),
        ("devices", "photo_url"),
        ("work_orders", "priority"),
        ("work_orders", "due_date"),
    ]

    print("\n🔍  Verificación de columnas:")
    all_ok = True
    for table, column in checks:
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table, column))
        exists = cursor.fetchone()[0] > 0
        status = "✅" if exists else "❌"
        print(f"  {status}  {table}.{column}")
        if not exists:
            all_ok = False

    cursor.close()
    conn.close()

    if all_ok:
        print("\n✅  Todas las columnas verificadas correctamente.")
    else:
        print("\n❌  Algunas columnas no existen. Revisa el log de migración.")

    return all_ok


if __name__ == "__main__":
    run_migrations()
    verify_columns()
