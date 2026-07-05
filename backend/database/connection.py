import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend_dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def migrate_password_column():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result] if result is not None else []
        if "password_hash" in columns and "password" not in columns:
            conn.execute(text("ALTER TABLE users RENAME TO users_old"))
            from . import models
            Base.metadata.create_all(bind=engine)
            conn.execute(text(
                "INSERT INTO users (id, username, email, password, created_at) "
                "SELECT id, username, email, password_hash, created_at FROM users_old"
            ))
            conn.execute(text("DROP TABLE users_old"))


def init_db():
    """Create database tables if they do not exist and migrate old schema."""
    from . import models
    migrate_password_column()
    Base.metadata.create_all(bind=engine)


def get_db():
    """Provide a database session for request handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
