from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os

USER = os.environ["PGUSER"]
PASSWORD = quote_plus(os.environ["PGPASSWORD"])
HOST = os.environ["PGHOST"]
PORT = os.environ.get("PGPORT", "5432")
DB = os.environ["PGDATABASE"]

url = f"postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

engine = create_engine(url, future=True)

with engine.connect() as conn:
    print(conn.execute(text("select 1")).scalar())