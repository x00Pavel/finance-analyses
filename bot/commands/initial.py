import logging

from email_validator import EmailNotValidError
from pydantic import validate_email

from bot.datatypes import CommandsEnum
from bot.db import User

welcome_msg = f"Please, use /{CommandsEnum.LOGIN.value} command to add your email ID to share the spreadsheets with it."
logger = logging.getLogger(__name__)


def register_initial_commands(bot):
    def email_handler(message):
        try:
            email = validate_email(message.text).email
            user = User(login=message.from_user.username, personal_email=email).save()
            bot.send_message(message.chat.id, f'Email {email} added to {user.login}')
        except EmailNotValidError as e:
            text = f'Email is not valid {e} Please, use /{CommandsEnum.LOGIN.value} command  again with valid email ' \
                   f'address.'
            bot.send_message(message.chat.id, text)

    @bot.message_handler(commands=[CommandsEnum.START.value, CommandsEnum.HELP.value])
    def send_welcome(message):
        bot.send_message(message.chat.id, welcome_msg)

    @bot.message_handler(commands=[CommandsEnum.LOGIN.value])
    def login(message):
        parts = message.text.split(' ')
        logger.debug('New logging attempt')
        if len(parts) < 2:
            msg = bot.send_message(message.chat.id, 'Please, provide email to share the spreadsheets with it.')
            bot.register_next_step_handler(msg, email_handler)
        else:
            message.text = parts[1]
            email_handler(message)

    logger.info('Initial commands registered')
