from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from shared.database.session import SessionLocal, engine


class DatabaseService:
    @staticmethod
    @contextmanager
    def session() -> Iterator[Session]:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL não está configurada")

        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def close() -> None:
        if engine is not None:
            engine.dispose()
