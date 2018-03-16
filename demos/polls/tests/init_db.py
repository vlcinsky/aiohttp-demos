import pathlib

from sqlalchemy import create_engine, MetaData
import yaml

from dpo_tis_journal.db import question, choice, user_journal

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"
BASE_DIR = pathlib.Path(__file__).parent.parent


def get_config(path):
    with open(path) as f:
        config = yaml.load(f)['postgres']
    return config


ADMIN_DB_URL = DSN.format(
    user='postgres',
    password='postgres',
    database='postgres',
    host='localhost',
    port=5432)

admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')

USER_CONFIG = get_config(BASE_DIR / 'config' / 'polls.yaml')
USER_DB_URL = DSN.format(**USER_CONFIG)
user_engine = create_engine(USER_DB_URL)

TEST_CONFIG = get_config(BASE_DIR / 'config' / 'polls_test.yaml')
TEST_DB_URL = DSN.format(**TEST_CONFIG)
test_engine = create_engine(TEST_DB_URL)


def setup_db(config):

    db_name = config['database']
    db_user = config['user']
    db_pass = config['password']

    conn = admin_engine.connect()
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
    conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" % (db_name,
                                                                db_user))
    conn.close()


def teardown_db(config):

    db_name = config['database']
    db_user = config['user']

    conn = admin_engine.connect()
    conn.execute("""
      SELECT pg_terminate_backend(pg_stat_activity.pid)
      FROM pg_stat_activity
      WHERE pg_stat_activity.datname = '%s'
        AND pid <> pg_backend_pid();""" % db_name)
    conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
    conn.execute("DROP ROLE IF EXISTS %s" % db_user)
    conn.close()


def create_tables(engine=test_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[question, choice, user_journal])


def drop_tables(engine=test_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[question, choice, user_journal])


def sample_data(engine=test_engine):
    conn = engine.connect()
    conn.execute(question.insert(), [{
        'question_text': 'What\'s new?',
        'pub_date': '2015-12-15 17:17:49.629+02'
    }])
    conn.execute(choice.insert(), [
        {
            'choice_text': 'Not much',
            'votes': 0,
            'question_id': 1
        },
        {
            'choice_text': 'The sky',
            'votes': 0,
            'question_id': 1
        },
        {
            'choice_text': 'Just hacking again',
            'votes': 0,
            'question_id': 1
        },
    ])
    conn.execute(user_journal.insert(), [
        {
            'dtime': '2015-12-15 17:17:49.629+02',
            'action': 'login',
            'user_name': 'javl'
        },
        {
            'dtime': '2015-12-15 17:17:52.629+02',
            'action': 'login',
            'user_name': 'pebu'
        },
        {
            'dtime': '2015-12-15 17:17:54.629+02',
            'action': 'login',
            'user_name': 'roho'
        },
    ])
    conn.close()


if __name__ == '__main__':

    setup_db(USER_CONFIG)
    create_tables(engine=user_engine)
    sample_data(engine=user_engine)
    # drop_tables()
    # teardown_db(config)
