import aiohttp_jinja2
from aiohttp import web

from dpo_tis_journal.marshall.question import QuestionSchema
from dpo_tis_journal.marshall.choice import ChoiceSchema
from dpo_tis_journal.marshall.user_journal import UserJournalSchema

from . import db


@aiohttp_jinja2.template('index.html')
async def index(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.question.select())
        records = await cursor.fetchall()
        questions = [dict(q) for q in records]
        return {'questions': questions}


@aiohttp_jinja2.template('detail.html')
async def poll(request):
    async with request.app['db'].acquire() as conn:
        question_id = request.match_info['question_id']
        try:
            question, choices = await db.get_question(conn, question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return {'question': question, 'choices': choices}


async def journal_poll(request):
    async with request.app['db'].acquire() as conn:
        question_id = request.match_info['question_id']
        try:
            question, choices = await db.get_question(conn, question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        res = {
            'question': QuestionSchema().dump(dict(question))[0],
            'choices': ChoiceSchema(many=True).dump(map(dict, choices))[0]
        }
        return web.json_response(res)


async def journal_user(request):
    async with request.app['db'].acquire() as conn:
        user_name = request.match_info.get('user_name')
        try:
            records = await db.get_user_journal(conn, user_name)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        res = UserJournalSchema(many=True).dump(map(dict, records))[0]
        return web.json_response(res)


@aiohttp_jinja2.template('results.html')
async def results(request):
    async with request.app['db'].acquire() as conn:
        question_id = request.match_info['question_id']

        try:
            question, choices = await db.get_question(conn, question_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))

        return {'question': question, 'choices': choices}


async def vote(request):
    async with request.app['db'].acquire() as conn:
        question_id = int(request.match_info['question_id'])
        data = await request.post()
        try:
            choice_id = int(data['choice'])
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text='You have not specified choice value') from e
        try:
            await db.vote(conn, question_id, choice_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        router = request.app.router
        url = router['results'].url_for(question_id=str(question_id))
        return web.HTTPFound(location=url)
