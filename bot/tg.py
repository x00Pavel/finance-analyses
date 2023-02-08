import logging

from telebot import TeleBot

from bot.commands import register_commands
from bot.config import TGConfig
from bot.google import GoogleSheet

logger = logging.getLogger(__name__)


def init_bot(config: TGConfig, gs: GoogleSheet):
    bot = TeleBot(config.token.get_secret_value(), threaded=True)
    if config.webhook_url:
        # bot.set_webhook(url=config.webhook_url)
        logger.info('Webhook is set %s.', config.webhook_url)
    else:
        logger.info('Webhook is not set. Bot will use polling.')
    register_commands(bot, gs)
    return bot
