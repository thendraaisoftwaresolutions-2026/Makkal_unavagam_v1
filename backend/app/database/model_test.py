import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import (
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
)


class TestModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):

    __tablename__ = "architecture_test"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


def test_model_architecture():

    print("Model table:", TestModel.__tablename__)

    print(
        "Primary key type:",
        TestModel.__table__.c.id.type
    )

    print(
        "Columns:",
        list(TestModel.__table__.columns.keys())
    )

    print(
        "Primary key:",
        TestModel.__table__.primary_key.columns.keys()
    )

    print(
        "UUID generated:",
        isinstance(uuid.uuid4(), uuid.UUID)
    )


if __name__ == "__main__":
    test_model_architecture()