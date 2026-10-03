from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

missing_variables = [
    name
    for name, value in (
        ("DB_HOST", DB_HOST),
        ("DB_PORT", DB_PORT),
        ("DB_USER", DB_USER),
        ("DB_PASSWORD", DB_PASSWORD),
        ("DB_NAME", DB_NAME),
    )
    if not value
]
if missing_variables:
    raise RuntimeError(
        "Missing required database environment variables: "
        f"{', '.join(missing_variables)}. Configure them in Railway Variables "
        "or in the local .env file."
    )

DB_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
