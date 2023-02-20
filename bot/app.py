import logging

import flask
from flask import Flask, request
from telebot.types import Update

from bot.config import Config
from bot.db import connect_db
from bot.google import GoogleSheet
from bot.tg import init_bot


logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    config = Config()
    connect_db(config.mongo)
    gs = GoogleSheet(config.gs)
    bot = init_bot(config.tg, gs)
    logger.info('Bot is ready to work.')

    @app.route('/')
    def index():
        if bot.get_webhook_info().url == '':
            return flask.redirect(f'/set_webhook/{bot.token}')
        return "OK"

    @app.route(f'/{bot.token}', methods=['POST'])
    def webhook():
        logger.debug('Received update: %s', request.json)
        update = Update.de_json(request.json)
        bot.process_new_updates([update])
        return "OK"

    @app.route(f'/set_webhook/{bot.token}', methods=['GET'])
    def set_webhook():
        if bot.get_webhook_info().url == '':
            url = request.url_root + bot.token
            url = url.replace('http://', 'https://')
            logger.info(f'Webhook url: {url}')
            try:
                s = bot.set_webhook(url=url)
            except Exception as e:
                logger.error(e)
                return e
            else:
                if s:
                    return "webhook setup ok"
                else:
                    return "webhook setup failed"
        else:
            return "webhook already setup"

    return app
