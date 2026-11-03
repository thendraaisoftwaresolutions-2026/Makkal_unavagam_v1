from app.database.base import Base
import app.models


def test_models():

    print("Registered database tables:")

    for table_name in Base.metadata.tables:
        print("-", table_name)

    print("\nTotal tables:", len(Base.metadata.tables))


if __name__ == "__main__":
    test_models()