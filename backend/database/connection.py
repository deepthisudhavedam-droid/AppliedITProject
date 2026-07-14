import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

engine = None
SessionLocal = None
Base = declarative_base()


def _get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./backend_dev.db")


def _get_engine():
    global engine, SessionLocal
    if engine is None:
        database_url = _get_database_url()
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


engine = _get_engine()


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
    _get_engine()
    from . import models
    migrate_password_column()
    Base.metadata.create_all(bind=engine)


def get_db():
    """Provide a database session for request handling."""
    _get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
