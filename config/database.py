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
DB_SSL_CA = os.getenv("DB_SSL_CA")

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
        f"{', '.join(missing_variables)}. Configure them in the hosting service "
        "or in the local .env file."
    )

DB_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

connect_args = {}
if DB_SSL_CA:
    connect_args = {
        "ssl_ca": DB_SSL_CA,
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
