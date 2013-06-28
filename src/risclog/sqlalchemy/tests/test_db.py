import pytest


def test_Database_is_able_to_handle_multiple_databases(
        database_1, database_2):
    from ..model import ObjectBase, declarative_base
    from sqlalchemy import Column, Integer
    from sqlalchemy.engine.reflection import Inspector

    class ObjectBase_1(ObjectBase):
        _engine_name = 'db1'
    Base_1 = declarative_base(ObjectBase_1)

    class Model_1(Base_1):
        id = Column(Integer, primary_key=True)

    class ObjectBase_2(ObjectBase):
        _engine_name = 'db2'
    Base_2 = declarative_base(ObjectBase_2)

    class Model_2(Base_2):
        id = Column(Integer, primary_key=True)

    database_1.create_all('db1')
    database_1.create_all('db2')

    # Tables are stored in different databases:
    inspector_1 = Inspector.from_engine(database_1.get_engine('db1'))
    assert ['tmp_functest', 'model_1'] == inspector_1.get_table_names()

    inspector_2 = Inspector.from_engine(database_2.get_engine('db2'))
    assert ['tmp_functest', 'model_2'] == inspector_2.get_table_names()


def test_Database_cannot_be_created_twice(database_1):
    from ..db import Database
    # The first time Database is created in fixture:
    with pytest.raises(AssertionError) as err:
        Database()
    assert str(err.value).startswith('Cannot create Database twice')


def test__verify_engine_checks_whether_the_correct_database_is_accessed(
        database_1):
    database_1.testing = False
    try:
        with pytest.raises(SystemExit) as err:
            database_1._verify_engine(database_1.get_engine('db1'))
    finally:
        database_1.testing = True
    assert str(err.value).startswith(
        'Not working against correct database (live vs testing).')


def test_get_database_returns_database_utility(database_1):
    from ..db import get_database, Database
    db = get_database(testing=True)
    assert isinstance(db, Database)


def test_get_database_makes_sure_testing_matches(database_1):
    from ..db import get_database
    with pytest.raises(AssertionError) as err:
        # In tests utility is set up with `testing=True`:
        get_database(testing=False)
    assert str(err.value) == 'Requested testing status `False` does not ' \
                             'match Database.testing.'
