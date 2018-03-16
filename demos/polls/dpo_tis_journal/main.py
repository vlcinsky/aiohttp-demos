import argparse
import logging
import sys

import jinja2

import aiohttp_jinja2
from aiohttp import web
from dpo_tis_journal.db import close_pg, init_pg
from dpo_tis_journal.middlewares import setup_middlewares
from dpo_tis_journal.routes import setup_routes
from dpo_tis_journal.utils import TRAFARET
from trafaret_config import commandline


def init(argv):
    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(ap,
                                          default_config='./config/polls.yaml')
    #
    # define your command-line arguments here
    #
    options = ap.parse_args(argv)

    config = commandline.config_from_options(options, TRAFARET)

    # setup application and extensions
    app = web.Application()

    # load config from yaml file in current dir
    app['config'] = config

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('dpo_tis_journal', 'templates'))

    # create connection to the database
    app.on_startup.append(init_pg)
    # shutdown db connection on exit
    app.on_cleanup.append(close_pg)
    # setup views and routes
    setup_routes(app)
    setup_middlewares(app)

    return app


def main(argv):
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    app = init(argv)
    web.run_app(app,
                host=app['config']['host'],
                port=app['config']['port'])


if __name__ == '__main__':
    main(sys.argv[1:])
