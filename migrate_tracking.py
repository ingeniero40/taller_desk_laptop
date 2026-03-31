"""
migrate_tracking.py
────────────────────
Migración — Módulo Seguimiento de Reparaciones (Contexto 5).

Tablas nuevas:
  work_order_comments   → comentarios internos y visibles al cliente
  work_order_incidents  → registro de problemas encontrados y soluciones

Uso:  python migrate_tracking.py
"""
import os, sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PGMESSAGELANG", "English")
load_dotenv()

MIGRATIONS = [
    {
        "desc": "CREATE TABLE work_order_comments",
        "sql": """
            CREATE TABLE IF NOT EXISTS work_order_comments (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
                work_order_id   UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
                author_id       UUID REFERENCES users(id) ON DELETE SET NULL,
                author_name     VARCHAR(150),
                content         TEXT NOT NULL,
                is_internal     BOOLEAN NOT NULL DEFAULT TRUE
            );
        """
    },
    {
        "desc": "INDEX idx_woc_order_id",
        "sql": "CREATE INDEX IF NOT EXISTS idx_woc_order_id ON work_order_comments(work_order_id);"
    },
    {
        "desc": "CREATE TABLE work_order_incidents",
        "sql": """
            CREATE TABLE IF NOT EXISTS work_order_incidents (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
                work_order_id   UUID NOT NULL REFERENCES work_orders(id) ON DELETE CASCADE,
                reported_by_id  UUID REFERENCES users(id) ON DELETE SET NULL,
                problem_found   TEXT NOT NULL,
                solution_applied TEXT,
                is_resolved     BOOLEAN NOT NULL DEFAULT FALSE,
                resolved_at     TIMESTAMP
            );
        """
    },
    {
        "desc": "INDEX idx_woi_order_id",
        "sql": "CREATE INDEX IF NOT EXISTS idx_woi_order_id ON work_order_incidents(work_order_id);"
    },
]

VERIFY_TABLES = ["work_order_comments", "work_order_incidents"]


def run():
    import psycopg2
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌  DATABASE_URL no encontrada en .env"); sys.exit(1)

    print("\n🗄️  Gravity — Migration: Tracking Module")
    print("─" * 44)
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
    conn.commit(); cur.close(); conn.close()
    print("─" * 44)
    print(f"✅  {ok}/{len(MIGRATIONS)} operaciones aplicadas.")
    _verify(db_url)


def _verify(db_url):
    import psycopg2
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    print("\n🔍  Verificación:")
    for tbl in VERIFY_TABLES:
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name=%s", (tbl,))
        ok = cur.fetchone()[0] > 0
        print(f"  {'✅' if ok else '❌'}  TABLE {tbl}")
    cur.close(); conn.close()
    print("─" * 44)


if __name__ == "__main__":
    run()
