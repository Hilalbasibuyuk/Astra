from database.questdb.query_connection import create_query_connection


def test_questdb_query_connection():
    with create_query_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

    assert result == (1,)