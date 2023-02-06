import logging
from datetime import datetime

from telebot import TeleBot, formatting
from os import environ

from bot.datatypes import Expanses, CommandsEnum
from bot.exceptions import BotException
from bot.google import GoogleSheet
from bot.db import store_user, User
from bot.helpers import date_format
from email_validator import validate_email, EmailNotValidError

bot = TeleBot(environ.get('TG_API_TOKEN'))
gs = GoogleSheet()
commands = {f'{CommandsEnum.START}': 'Start bot'}

welcome_msg = f"Please, use /{CommandsEnum.LOGIN.value} command to add your email ID to share the spreadsheets with it."


@bot.message_handler(commands=[CommandsEnum.START.value, CommandsEnum.HELP.value])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome_msg)


@bot.message_handler(commands=[CommandsEnum.LOGIN.value])
def login(message):
    parts = message.text.split(' ')
    if len(parts) < 2:
        msg = bot.send_message(message.chat.id, 'Please, provide email to share the spreadsheets with it.')
        bot.register_next_step_handler(msg, email_handler)
    else:
        message.text = parts[1]
        email_handler(message)


def email_handler(message):
    try:
        email = validate_email(message.text).email
        user = User(login=message.from_user.username, personal_email=email).save()
        bot.send_message(message.chat.id, f'Email {email} added to {user.login}')
    except EmailNotValidError as e:
        text = f'Email is not valid {e} Please, use /{CommandsEnum.LOGIN.value} command  again with valid email address.'
        bot.send_message(message.chat.id, text)


def get_month(text):
    parts = text.split(' ')
    return int(parts[1]) if len(parts) > 1 else None


@bot.message_handler(commands=[CommandsEnum.NEW.value])
def new_sheet(message):
    month = get_month(message.text)
    gs.create_sheet(month)


@bot.message_handler(commands=[CommandsEnum.ADD.value])
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


@bot.message_handler(commands=[CommandsEnum.ADD_EMAIL.value])
def add_email(message):
    def email_adder(emails: list[str]):
        result_emails = []
        for email in emails:
            try:
                validation = validate_email(email)
                result_emails.append(validation.email)
            except EmailNotValidError as e:
                bot.send_message(message.chat.id, f'Email {email} is not valid: {e}')
        result = User.objects(_id=message.from_user.username).first().add_additional_email(result_emails)
        bot.send_message(message.chat.id, result.to_json())

    parts: list[str] = message.text.split(' ')
    if CommandsEnum.ADD_EMAIL.value not in parts:
        email_adder(parts)
    elif len(parts) < 2:
        msg = bot.send_message(message.chat.id, 'Please, provide additional email(s) to share the spreadsheets with it.')
        bot.register_next_step_handler(msg, email_handler)
    else:
        email_adder(parts[1:])
