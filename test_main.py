import pytest

from uuid import UUID

from pydantic.error_wrappers import ValidationError

from main import Email, ContactSchema, ContactModel, Id

def test_email_schema():
    email = Email(value='test@email.com')

    assert email.value == 'test@email.com'


def test_contact_schema_id_as_dict():
    contact = ContactSchema(
        **{
            'id': {'value': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'},
            'email': {'value': 'test@email.com'}
        }
    )

    assert contact.id == Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    assert contact.email.value == 'test@email.com'


def test_contact_schema_id_as_str():
    contact = ContactSchema(
        **{
            'id': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
            'email': {'value': 'test@email.com'}
        }
    )

    assert contact.id == Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    assert contact.email.value == 'test@email.com'


def test_contact_schema_email_as_dict():
    contact = ContactSchema(
        **{
            'id': {'value': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'},
            'email': 'test@email.com'
        }
    )

    assert contact.id == Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    assert contact.email.value == 'test@email.com'


def test_contact_schema_both_as_string():
    contact = ContactSchema(
        **{
            'id': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
            'email': 'test@email.com'
        }
    )

    assert contact.id == Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    assert contact.email.value == 'test@email.com'

def test_contact_schema_both_as_dict():
    contact = ContactSchema(
        **{
            'id': {'value': 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'},
            'email': {'value': 'test@email.com'}
        }
    )

    assert contact.id == Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    assert contact.email.value == 'test@email.com'


def test_contact_schema_email_as_str():
    contact = ContactSchema(
        **{
            'id': Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')),
            'email': 'test@email.com'
        }
    )

    assert contact.id == Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    assert contact.email.value == 'test@email.com'


def test_contact_schema_dict_representation():
    contact = ContactSchema(
        id=Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')),
        email='test@email.com'
    )

    assert contact.dict() == {
            'id': {'value': UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')},
            'email': {'value': 'test@email.com'}
        }


def test_contact_schema_json_representation():
    contact = ContactSchema(
        id=Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')),
        email='email@test.com'
    )

    assert contact.json(models_as_dict=False) == '{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "email": "email@test.com"}'
    assert contact.json() == '{"id": {"value": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"}, "email": {"value": "email@test.com"}}'


def test_contact_schema_raises_when_id_empty_string():

    with pytest.raises(ValidationError) as e:
        contact = ContactSchema(
            id='',
            email='test@email.com'
        )

    assert 'value cannot be empty' in str(e.value)


def test_contact_schema_raises_when_email_empty_string():

        with pytest.raises(ValidationError) as e:
            contact = ContactSchema(
                id=Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')),
                email=''
            )

        assert 'value cannot be empty' in str(e.value)


def test_contact_schema_from_model_sqlite(session_sqlite):
    ex_id = Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    ex_email = Email(value='test@email.com')

    contact = ContactModel(
        id=ex_id,
        email=ex_email
    )

    with session_sqlite:
        session_sqlite.add(contact)
        session_sqlite.commit()

        model = session_sqlite.query(ContactModel).first()

        expected = ContactSchema.from_orm(model)

    assert isinstance(expected, ContactSchema)
    assert isinstance(expected.id, Id)
    assert isinstance(expected.email, Email)
    assert expected.id == ex_id
    assert expected.email == ex_email
    assert expected.id.value == UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    assert expected.email.value == 'test@email.com'


def test_contact_schema_from_model_postgres(session_postgres):
    ex_id = Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'))
    ex_email = Email(value='test@email.com')

    contact = ContactModel(
        id=ex_id,
        email=ex_email
    )

    session_postgres.add(contact)
    session_postgres.commit()

    model = session_postgres.query(ContactModel).first()

    expected = ContactSchema.from_orm(model)

    assert isinstance(expected, ContactSchema)
    assert isinstance(expected.id, Id)
    assert isinstance(expected.email, Email)
    assert expected.id == ex_id
    assert expected.email == ex_email
    assert expected.id.value == UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    assert expected.email.value == 'test@email.com'


def test_contact_model_creation_sqlite(session_sqlite):
    contact = ContactModel(
        id=Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')),
        email=Email(value='test@email.com')
    )

    session_sqlite.add(contact)
    session_sqlite.commit()

    expected = session_sqlite.query(ContactModel).first()

    assert session_sqlite.query(ContactModel).count() == 1
    assert expected.id.value == UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    assert expected.email.value == 'test@email.com'


def test_contact_model_creation_postgres(session_postgres):
    contact = ContactModel(
        id=Id(value=UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')),
        email=Email(value='test@email.com')
    )

    session_postgres.add(contact)
    session_postgres.commit()

    expected = session_postgres.query(ContactModel).first()
    count = session_postgres.query(ContactModel).count()

    assert count == 1
    assert expected.id.value == UUID('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
    assert expected.email.value == 'test@email.com'

