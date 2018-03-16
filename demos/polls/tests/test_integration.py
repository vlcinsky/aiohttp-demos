"""Require running database server"""

from dpo_tis_journal.db import choice


async def test_index(cli, tables_and_data):
    response = await cli.get('/')
    assert response.status == 200
    resp_text = await response.text()
    assert 'Main' in resp_text
    assert 'What' in resp_text
    assert 'new?' in resp_text


async def test_results(cli, tables_and_data):
    response = await cli.get('/poll/1/results')
    assert response.status == 200
    assert 'Just hacking again' in await response.text()


async def test_vote(cli, tables_and_data):

    question_id = 1
    choice_text = 'Not much'

    async with cli.server.app['db'].acquire() as conn:
        res = await conn.execute(
            choice.select(
            ).where(choice.c.question_id == question_id)
             .where(choice.c.choice_text == choice_text)
        )
        not_much_choice = await res.first()
        not_much_choice_id = not_much_choice.id
        votes_before = not_much_choice.votes

        response = await cli.post(
            f'/poll/{question_id}/vote',
            data={'choice': not_much_choice_id}
        )
        assert response.status == 200

        res = await conn.execute(
            choice.select(
            ).where(choice.c.question_id == question_id)
             .where(choice.c.choice_text == choice_text)
        )
        not_much_choice = await res.first()
        votes_after = not_much_choice.votes

        assert votes_after == votes_before + 1
