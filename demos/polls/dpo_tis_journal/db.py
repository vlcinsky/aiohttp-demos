import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, DateTime
)

__all__ = ['question', 'choice', 'user_journal']

meta = MetaData()

user_journal = Table(
    'user_journal', meta,

    Column('dtime', DateTime),
    Column('action', String(200), nullable=False),
    Column('user_name', String(30), nullable=False)
)

question = Table(
    'question', meta,
    Column('id', Integer, primary_key=True),
    Column('question_text', String(200), nullable=False),
    Column('pub_date', Date, nullable=False)
)

choice = Table(
    'choice', meta,

    Column('id', Integer, primary_key=True),
    Column('choice_text', String(200), nullable=False),
    Column('votes', Integer, server_default="0", nullable=False),

    Column('question_id',
           Integer,
           ForeignKey('question.id', ondelete='CASCADE'))
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_user_journal(conn, user_name=None):
    query = user_journal.select()
    if user_name:
        query = query.where(user_journal.c.user_name == user_name)
    query = query.order_by(user_journal.c.dtime)
    result = await conn.execute(query)
    records = await result.fetchall()
    return records


async def get_question(conn, question_id):
    result = await conn.execute(
        question.select()
        .where(question.c.id == question_id))
    question_record = await result.first()
    if not question_record:
        msg = "Question with id: {} does not exists"
        raise RecordNotFound(msg.format(question_id))
    result = await conn.execute(
        choice.select()
        .where(choice.c.question_id == question_id)
        .order_by(choice.c.id))
    choice_records = await result.fetchall()
    return question_record, choice_records


async def vote(conn, question_id, choice_id):
    result = await conn.execute(
        choice.update()
        .returning(*choice.c)
        .where(choice.c.question_id == question_id)
        .where(choice.c.id == choice_id)
        .values(votes=choice.c.votes+1))
    record = await result.fetchone()
    if not record:
        msg = "Question with id: {} or choice id: {} does not exists"
        raise RecordNotFound(msg.format(question_id, choice_id))
