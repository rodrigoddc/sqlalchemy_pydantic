import uuid
from typing import Union

from pydantic.class_validators import validator
from pydantic.main import BaseModel
from sqlalchemy import String, Uuid, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Id(BaseModel):
    __hash__ = object.__hash__
    id_value: uuid.UUID

    class Config:
        orm_mode = True
        validate_assignment = True


class Email(BaseModel):
    __hash__ = object.__hash__
    email_value: str

    class Config:
        orm_mode = True
        validate_assignment = True


class IdType(TypeDecorator):
    impl = Uuid

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(String(36))
        else:
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Id):
            if dialect.name == 'sqlite':
                return str(value.id_value)
            else:
                return value.id_value

    def process_result_value(self, value: Union[str, None], dialect) -> Union[Id, None]:
        if value is None:
            return None
        elif isinstance(value, str):
            # on sqlite is saved as string
            return Id(id_value=uuid.UUID(value))
        return Id(id_value=value)


class EmailType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Email):
            return value.email_value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Email(email_value=value)


class Base(DeclarativeBase):
    type_annotation_map = {
        Id: IdType,
        Email: EmailType,
    }


def id_parser(value: str | uuid.UUID) -> uuid.UUID:
    if not value:
        raise ValueError("value cannot be empty")
    elif isinstance(value, str):
        return uuid.UUID(value)
    return value


def email_parser(value: str | dict) -> dict:
    if isinstance(value, str) and not value:
        raise ValueError("value cannot be empty")
    elif isinstance(value, str):
        return {'email_value': value}
    return value


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[Id] = mapped_column(IdType, primary_key=True)
    email: Mapped[Email] = mapped_column(EmailType, nullable=False, unique=True)

    _parse_id = validator("id", pre=True, allow_reuse=True, always=True)(id_parser)
    _parse_email = validator("email", pre=True, allow_reuse=True, always=True)(email_parser)

