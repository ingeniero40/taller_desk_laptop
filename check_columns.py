import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def check():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    engine = create_engine(db_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name, ordinal_position FROM information_schema.columns WHERE table_name = 'products' ORDER BY ordinal_position;"))
        for row in res:
            print(row)

if __name__ == "__main__":
    check()
