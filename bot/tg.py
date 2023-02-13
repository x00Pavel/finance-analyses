import logging

from telebot import TeleBot

from bot.commands import register_commands
from bot.config import TGConfig
from bot.google import GoogleSheet

logger = logging.getLogger(__name__)


def init_bot(config: TGConfig, gs: GoogleSheet):
    bot = TeleBot(config.token.get_secret_value(), threaded=True)
    register_commands(bot, gs)
    return bot
