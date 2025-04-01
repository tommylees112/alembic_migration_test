import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env
load_dotenv()

# Create base class for declarative models
Base = declarative_base()

# Define database connection using environment variables
DB_USER = os.getenv("DB_USER", "tommy")
DB_PASS = os.getenv("DB_PASS", "1234")
DB_NAME = os.getenv("DB_NAME", "alembic_migrate")
DB_HOST = os.getenv("DB_HOST", "localhost")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Helper function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import models to register them with SQLAlchemy
from alembic_migrate.models.models import ActiveUser, Post, User
