import pathlib

from .views import index, poll, results, vote
from .views import journal_poll, journal_user

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/poll/{question_id}', poll, name='poll')
    app.router.add_get(
        '/journal/poll/{question_id}', journal_poll, name='journal_poll')
    app.router.add_get(
        '/journal/user', journal_user, name='journal_user_all')
    app.router.add_get(
        '/journal/user/{user_name}', journal_user, name='journal_user')
    app.router.add_get('/poll/{question_id}/results', results, name='results')
    app.router.add_post('/poll/{question_id}/vote', vote, name='vote')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static(
        '/static/', path=PROJECT_ROOT / 'static', name='static')
