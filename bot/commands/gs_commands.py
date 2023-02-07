import logging
from datetime import datetime

from telebot import formatting

from bot.datatypes import CommandsEnum, Expanses
from bot.db import get_user
from bot.exceptions import BotException
from bot.google import GoogleSheet
from bot.helpers import date_format

logger = logging.getLogger(__name__)


def get_month(text):
    parts = text.split(' ')
    return int(parts[1]) if len(parts) > 1 else None


def register_gs_commands(bot, gs: GoogleSheet):
    @bot.message_handler(commands=[CommandsEnum.NEW.value])
    def new_sheet(message):
        month = get_month(message.text)
        user = get_user(message.from_user.username)
        if not user:
            msg = f'Please, provide your email with {CommandsEnum.LOGIN.value} ' \
                  'command to share the spreadsheet with it.'
            bot.send_message(message.chat.id, msg)
        else:
            gs.create_sheet(user, month)

    @bot.message_handler(commands=[CommandsEnum.ADD.value])
    def add_expense(message):
        try:
            user = get_user(message.from_user.username)
            if not user:
                raise BotException(f'You are not logged in. Please, use /{CommandsEnum.LOGIN.value} for this')
            expanse = Expanses(user, message.text)
            if expanse.date.month > datetime.today().month:
                raise BotException(f'Date is in the future {expanse.date.strftime(date_format)}')

            gs.write_expanse(expanse)
            bot.reply_to(message, f"Added {expanse}")
        except BotException as e:
            logger.exception(e)
            bot.reply_to(message, e.msg + '\nPlease, try again')
        except Exception as e:
            bot.reply_to(message, f'Unexpected exception is raised: {formatting.mbold(e)}')

    logger.info('Google Sheets commands registered')
