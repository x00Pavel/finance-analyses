import logging

from telebot import TeleBot

from bot.commands import register_commands
from bot.config import TGConfig
from bot.datatypes import commands_description
from bot.google import GoogleSheet

logger = logging.getLogger(__name__)


def init_bot(config: TGConfig, gs: GoogleSheet):
    bot = TeleBot(config.token.get_secret_value(), threaded=True)
    bot.delete_webhook()
    if config.webhook_url:
        logger.debug('Webhook url is set. Setting webhook.')
        url = '/'.join(i.strip("/") for i in [config.webhook_url, bot.token])
        logger.info(f'Setting webhook to {url}')
        bot.set_webhook(url=url)
    if bot.delete_my_commands():
        logger.debug('Commands are deleted')
    else:
        logger.warning('Commands are not deleted')
    if bot.set_my_commands(commands_description):
        logger.debug('Commands are set')
    else:
        logger.warning('Commands are not set')
    register_commands(bot, gs)
    return bot
