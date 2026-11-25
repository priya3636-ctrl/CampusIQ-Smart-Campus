import os

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

try:
    from sqlalchemy import create_engine  # type: ignore[import-not-found]
    from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "SQLAlchemy is required. Install it with 'pip install sqlalchemy psycopg2-binary python-dotenv'."
    ) from exc

# Load environment variables from backend/.env
load_dotenv()

# PostgreSQL connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from the .env file")

# Create PostgreSQL engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


# Database connection dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()