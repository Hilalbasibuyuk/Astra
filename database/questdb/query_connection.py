import psycopg

from apps.config import settings


def create_query_connection():
    return psycopg.connect(
        host=settings.questdb_host,
        port=settings.questdb_pg_port,
        user="admin",
        password="quest",
        dbname="qdb",
    )