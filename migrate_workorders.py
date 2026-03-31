"""
migrate_workorders.py
─────────────────────
Migración segura — Módulo Órdenes de Trabajo (Contexto 4).

Cambios:
  work_orders   → estimated_hours, actual_hours, actual_delivery
  work_order_history  → tabla nueva de auditoría

Uso:
    python migrate_workorders.py
"""

import os, sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PGMESSAGELANG", "English")
load_dotenv()

MIGRATIONS = [
    # ── work_orders nuevas columnas de tiempo ──────────────────────────────
    {
        "desc": "work_orders → estimated_hours FLOAT",
        "sql": "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS estimated_hours FLOAT;"
    },
    {
        "desc": "work_orders → actual_hours FLOAT",
        "sql": "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS actual_hours FLOAT;"
    },
    {
        "desc": "work_orders → actual_delivery TIMESTAMP",
        "sql": "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS actual_delivery TIMESTAMP;"
    },

    # ── tabla de historial de cambios ─────────────────────────────────────
    {
        "desc": "CREATE TABLE work_order_history",
        "sql": """
            CREATE TABLE IF NOT EXISTS work_order_history (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
                work_order_id   UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
                changed_by_id   UUID REFERENCES users(id) ON DELETE SET NULL,
                from_status     VARCHAR(30),
                to_status       VARCHAR(30) NOT NULL,
                notes           TEXT,
                changed_at      TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """
    },
    {
        "desc": "INDEX idx_woh_order_id",
        "sql": "CREATE INDEX IF NOT EXISTS idx_woh_order_id ON work_order_history(work_order_id);"
    },
]

VERIFY = [
    ("work_orders", "estimated_hours"),
    ("work_orders", "actual_hours"),
    ("work_orders", "actual_delivery"),
]

VERIFY_TABLES = ["work_order_history"]


def run():
    import psycopg2
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌  DATABASE_URL no encontrada en .env"); sys.exit(1)

    print("\n🗄️  Gravity — Migration: Work Orders Module")
    print("─" * 46)

    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()
    ok = 0

    for m in MIGRATIONS:
        try:
            print(f"  ▶  {m['desc']} ...", end=" ")
            cur.execute(m["sql"])
            print("✅")
            ok += 1
        except Exception as e:
            print(f"❌  {e}")
            conn.rollback(); cur.close(); conn.close(); sys.exit(1)

    conn.commit()
    cur.close()
    conn.close()

    print("─" * 46)
    print(f"✅  {ok}/{len(MIGRATIONS)} operaciones aplicadas.")
    _verify(db_url)


def _verify(db_url):
    import psycopg2
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    print("\n🔍  Verificación:")

    for table, col in VERIFY:
        cur.execute(
            "SELECT COUNT(*) FROM information_schema.columns WHERE table_name=%s AND column_name=%s",
            (table, col)
        )
        ok = cur.fetchone()[0] > 0
        print(f"  {'✅' if ok else '❌'}  {table}.{col}")

    for tbl in VERIFY_TABLES:
        cur.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", (tbl,)
        )
        ok = cur.fetchone()[0] > 0
        print(f"  {'✅' if ok else '❌'}  TABLE {tbl}")

    cur.close(); conn.close()
    print("─" * 46)


if __name__ == "__main__":
    run()
