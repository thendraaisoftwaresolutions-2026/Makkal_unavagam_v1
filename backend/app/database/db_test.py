from sqlalchemy import text
from app.database.connection import engine


def test_database_connection():

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT current_database(), current_user")
            )

            database, user = result.fetchone()

            print("Database connection successful!")
            print("Database:", database)
            print("Connected user:", user)

    except Exception as error:

        print("Database connection failed!")
        print("Error type:", type(error).__name__)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_database_connection()