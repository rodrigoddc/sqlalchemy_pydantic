import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import Base


@pytest.fixture(scope='function')
def engine_sqlite():
    engine = create_engine('sqlite:///sqlite.db', echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def session_sqlite(engine_sqlite):
    Session = sessionmaker(bind=engine_sqlite)
    with Session() as session:
        session.commit()
        yield session
        session.rollback()
        session.close()


@pytest.fixture(scope='function')
def engine_postgres():
    engine = create_engine(
        'postgresql://fleetplanning_user:OmgPassword!@localhost:5433/fleetplanning_db',
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def session_postgres(engine_postgres):
    Session = sessionmaker(bind=engine_postgres)
    with Session() as session:
        
        session.commit()
        yield session
        session.rollback()
        session.close()
