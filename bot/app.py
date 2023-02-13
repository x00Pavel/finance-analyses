import logging

from flask import Flask, request
from telebot.types import Update

from bot.config import Config
from bot.db import connect_db
from bot.google import GoogleSheet
from bot.tg import init_bot

logger = logging.getLogger(__name__)


def create_app(bot):
    app = Flask(__name__)

    @app.route(f'/{bot.token}', methods=['POST'])
    def handle():
        data = request.get_json()
        update = Update.de_json(data)
        bot.process_new_updates([update])
        return "OK"
    return app


def start_app(config, bot):
    logger.info('Starting the app')
    bot.remove_webhook()
    if config.tg.webhook_url:
        complete_url = f'{config.tg.webhook_url}/{bot.token}'
        app = create_app(bot)
        bot.set_webhook(url=complete_url)
        logger.info('Webhook is set %s.', complete_url)
        app.run(host='0.0.0.0', port=config.tg.webhook_port)
    else:
        logger.info('Webhook is not set. Bot will use polling.')
        bot.infinity_polling()


def main():
    config = Config()
    connect_db(config.mongo)
    gs = GoogleSheet(config.gs_creds)
    bot = init_bot(config.tg, gs)
    logger.info('Bot is ready to work.')
    start_app(config, bot)

