from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aptiverse:aptiverse123@db:5432/aptiverse_db"
)

# Create engine with SSL support for Neon.tech and connection pooling
# Neon.tech requires SSL connections in production
engine_args = {
    "pool_size": 10,  # Number of persistent connections
    "max_overflow": 20,  # Max additional connections
    "pool_pre_ping": True,  # Verify connections before using
    "pool_recycle": 3600,  # Recycle connections after 1 hour
}

if "neon.tech" in DATABASE_URL or "sslmode=require" in DATABASE_URL:
    # For Neon.tech or any database requiring SSL
    engine_args["connect_args"] = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
