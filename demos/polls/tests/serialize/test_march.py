import pytest
import datetime
from aiohttpdemo_polls.marshall.question import QuestionSchema
from aiohttpdemo_polls.marshall.choice import ChoiceSchema


@pytest.fixture
def choice_lst():
    return [{
        "id": 1,
        "choice_text": 'Not much',
        "votes": 1,
        "question_id": 1
    }, {
        "id": 2,
        "choice_text": 'The sky',
        "votes": 7,
        "question_id": 1
    }, {
        "id": 3,
        "choice_text": 'Just hacking again',
        "votes": 1,
        "question_id": 1
    }]


@pytest.fixture
def question():
    return {
        "id": 1,
        "question_text": "What's new?",
        "pub_date": datetime.date(2015, 12, 15)
    }


def test_question(question):
    res, errors = QuestionSchema().dump(question)
    assert res
    assert not errors


def test_choices(choice_lst):
    res, errors = ChoiceSchema(many=True).dump(choice_lst)
    assert res
    assert not errors
