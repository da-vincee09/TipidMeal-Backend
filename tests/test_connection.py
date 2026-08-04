from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:Rosario2005moon0919@db.wtqjxawnswjrprvbiivq.supabase.co:5432/postgres?sslmode=require"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("✅ Connected!")
        print(result.fetchone())
except Exception as e:
    print("❌ Error:")
    print(e)