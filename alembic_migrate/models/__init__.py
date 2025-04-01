import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for declarative models
Base = declarative_base()

# Define database connection - update with your actual Postgres credentials
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/dbname")

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
