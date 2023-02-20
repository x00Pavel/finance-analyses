import logging

from email_validator import EmailNotValidError, validate_email


from bot.datatypes import CommandsEnum
from bot.db import User, get_user

logger = logging.getLogger(__name__)


def register_emails_commands(bot):
    def email_adder(message):
        logger.debug('Adding emails')
        result_emails = []
        emails = message.text.split(' ')
        for email in emails:
            try:
                validation = validate_email(email)
                result_emails.append(validation.email)
            except EmailNotValidError as e:
                bot.send_message(message.chat.id, f'Email {email} is not valid: {e}')
        result = get_user(message.from_user).add_additional_email(result_emails)
        logger.debug('Update result: %s', result)
        msg = f'Emails are updated to {result.additional_emails}'
        logger.debug('Sending message: %s', msg)
        bot.send_message(message.chat.id, msg)

    @bot.message_handler(commands=[CommandsEnum.ADD_EMAIL.value])
    def add_email(message):
        parts: list[str] = message.text.split(' ', 1)
        if len(parts) < 2:
            msg = bot.send_message(message.chat.id,
                                   'Please, provide additional email(s) to share the spreadsheets with it.')
            bot.register_next_step_handler(msg, email_adder)
        else:
            message.text = parts[1]
            email_adder(message)

    logger.info('Emails commands registered')
