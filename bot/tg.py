import logging
from datetime import datetime

from telebot import TeleBot, formatting
from os import environ

from bot.datatypes import Expanses
from bot.exceptions import BotException
from bot.google import GoogleSheet

bot = TeleBot(environ.get('TG_API_TOKEN'))
gs = GoogleSheet()
date_format = '%d.%m.%Y'


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Howdy, how are you doing?")


def get_month(text):
    parts = text.split(' ')
    return int(parts[1]) if len(parts) > 1 else None


@bot.message_handler(commands=['new'])
def new_sheet(message):
    month = get_month(message.text)
    gs.create_sheet(month)


@bot.message_handler(commands=['add'])
def add_expense(message):
    try:
        expanse = Expanses(message.text)
        if expanse.date.month > datetime.today().month:
            # bot.send_message(message.chat.id, f'Date is in the future {expanse.date.strftime(date_format)}. '
            #                                    'Do you want to create a new sheet?',
            #                  reply_markup=gen_yes_no_keyboard())
            raise BotException(f'Date is in the future {expanse.date.strftime(date_format)}')

        gs.write_expanse(expanse)
        bot.reply_to(message, f"Added {expanse}")
    except BotException as e:
        logging.exception(e)
        bot.reply_to(message, e.msg + '\nPlease, try again')
    except Exception as e:
        bot.reply_to(message, f'Unexpected exception is raised: {formatting.mbold(e)}')
