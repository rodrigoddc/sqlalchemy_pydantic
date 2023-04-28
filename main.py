import uuid
from typing import Union

from pydantic.class_validators import validator
from pydantic.main import BaseModel
from sqlalchemy import String, Uuid, create_engine, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker, mapped_column

engine = create_engine("sqlite:///:memory:", echo=True)
session = sessionmaker(bind=engine)()
engine_postgres = create_engine(
    'postgresql://fleetplanning_user:OmgPassword!@localhost:5433/fleetplanning_db',
)
session_postgres = sessionmaker(bind=engine_postgres)()


class Id(BaseModel):
    __hash__ = object.__hash__
    value: uuid.UUID

    class Config:
        orm_mode = True
        validate_assignment = True


class Email(BaseModel):
    __hash__ = object.__hash__
    value: str

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
                return str(value.value)
            else:
                return value.value

    def process_result_value(self, value: Union[str, None], dialect) -> Union[Id, None]:
        if value is None:
            return None
        elif isinstance(value, str):
            # on sqlite is saved as string
            return Id(value=uuid.UUID(value))
        return Id(value=value)


class EmailType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Email):
            return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Email(value=value)


class Base(DeclarativeBase):
    type_annotation_map = {
        Id: IdType,
        Email: EmailType,
    }


class ContactModel(Base):
    __tablename__ = "contacts"

    # Tambem pode ser feito omitindo o sqlalchemy type customizado,
    # uma vez que este esta mapeado no Base.type_annotation_map
    # id = mapped_column(primary_key=True)
    # email = mapped_column(nullable=False, unique=True)
    id: Mapped[Id] = mapped_column(IdType, primary_key=True)
    email: Mapped[Email] = mapped_column(EmailType, nullable=False, unique=True)


def default_parser(value: str | dict) -> dict:
    """
    Permite que a classe Contact possa ser instanciada com um dicionario
    tal que os atributos compostos (ex: Id, Email) possam receber como valor
    apenas uma string, ou ou dicionario que represente o valor do atributo composto.

        e.g.:
            {'id': '123e4567-e89b-12d3-a456-426614174000'}
            ou
            {'id': {'value': '123e4567-e89b-12d3-a456-426614174000'}}
    :param value:
    :return:
    """
    if isinstance(value, str) and not value:
        raise ValueError("value cannot be empty")
    if isinstance(value, str) or isinstance(value, uuid.UUID):
        return {'value': value}
    return value


class ContactSchema(BaseModel):
    id: Id
    email: Email

    class Config:
        orm_mode = True
        json_encoders = {
            Id: lambda v: str(v.value),
            Email: lambda v: v.value,
        }

    _parse_id = validator("id", pre=True, allow_reuse=True)(default_parser)
    _parse_email = validator("email", pre=True, allow_reuse=True)(default_parser)
