import json
import logging
import random
import string

import aiohttp_jinja2
import aiohttp
from aiohttp import web


log = logging.getLogger(__name__)


async def index(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)
    name = (random.choice(string.ascii_uppercase) +
            ''.join(random.sample(string.ascii_lowercase*10, 10)))
    log.info('%s joined.', name)
    await ws_current.send_str(json.dumps({'action': 'connect',
                                          'name': name}))
    for ws in request.app['websockets'].values():
        await ws.send_str(json.dumps({'action': 'join',
                                      'name': name}))
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_str(json.dumps({'action': 'sent',
                                                  'name': name,
                                                  'text': msg.data}))
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_str(json.dumps({'action': 'disconnect',
                                      'name': name}))
    return ws_current


def setup(app):
    app.router.add_get('/', index)
