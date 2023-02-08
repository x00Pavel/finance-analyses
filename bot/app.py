import logging

from bot.config import Config
from bot.db import connect_db
from bot.google import GoogleSheet
from bot.tg import init_bot

logger = logging.getLogger(__name__)


def main():
    config = Config()
    connect_db(config.mongo)
    gs = GoogleSheet(config.gs_creds)
    bot = init_bot(config.tg, gs)
    logger.info('Bot is ready to work.')
    try:
        if config.tg.webhook_url:
            bot.run_webhooks(webhook_url=config.tg.webhook_url, port=5000)
        else:
            bot.remove_webhook()
            bot.infinity_polling()
    finally:
        bot.stop_bot()
