from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from one_class import Contact, Id, Email


def test_contact_model_creation_sqlite(session_sqlite):
    t_id = Id(id_value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    t_email = Email(email_value='test@email.com')

    contact = Contact(
        id=t_id,
        email=t_email
    )

    session_sqlite.add(contact)
    session_sqlite.commit()

    expected = session_sqlite.query(Contact).first()

    assert session_sqlite.query(Contact).count() == 1
    assert isinstance(expected.id.id_value, UUID)
    assert expected.id.id_value == UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    assert expected.email.email_value == 'test@email.com'


def test_contact_model_creation_postgres(session_postgres):
    t_id = Id(id_value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    t_email = Email(email_value='test@email.com')

    contact = Contact(
        id=t_id,
        email=t_email
    )

    session_postgres.add(contact)
    session_postgres.commit()

    expected = session_postgres.query(Contact).first()

    assert session_postgres.query(Contact).count() == 1
    assert isinstance(expected.id.id_value, UUID)
    assert expected.id.id_value == UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    assert expected.email.email_value == 'test@email.com'


