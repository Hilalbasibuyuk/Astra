from sqlalchemy import text

from database.postgres.connection import engine


def test_postgres_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar() == 1