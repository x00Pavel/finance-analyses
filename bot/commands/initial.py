import logging

from email_validator import EmailNotValidError, validate_email
from telebot.types import Message

from bot.datatypes import CommandsEnum
from bot.storage.db import User

welcome_msg = """
Hello! I'm a bot and my mission is to help you to track your expenses.
On your first login I will create a spreadsheet for you.
This spreadsheet I will use for adding your expanses for this year (new file for each year :).
So, after login check your inbox for the email from Google with the link to the spreadsheet. 

You can use **Menu** button to navigate through the commands.
To see more details about the command use /help <command_name> or check the documentation on official website.

Quick help how to start:
1. /login - to provide your email to the bot and create a spreadsheet for you
2. /add_category - to add categories for your expanses
3. /add - to add new expense
4. Check your email for the link to the spreadsheet
5. Keep tracking your expanses :)
"""

logger = logging.getLogger(__name__)


def register_initial_commands(bot):
    def email_handler(message: Message):
        try:
            email = validate_email(message.text).email
            user = User(
                login=message.from_user.username or str(message.from_user.id),
                personal_email=email,
            ).save()
            bot.send_message(message.chat.id, f"Email {email} added to {user.login}")
        except EmailNotValidError as e:
            text = (
                f"Email is not valid {e} Please, use /{CommandsEnum.LOGIN.value} command  again with valid email "
                f"address."
            )
            logger.debug(f"Email is not valid {e}")
            bot.send_message(message.chat.id, text)

    @bot.message_handler(commands=[CommandsEnum.START.value, CommandsEnum.HELP.value])
    def send_welcome(message):
        bot.send_message(message.chat.id, welcome_msg)

    @bot.message_handler(commands=[CommandsEnum.LIST.value])
    def list_commands(message):
        cmd_list = "\n".join([f"/{c.value}" for c in CommandsEnum])
        bot.send_message(message.chat.id, f"Available commands:\n{cmd_list}")

    @bot.message_handler(commands=[CommandsEnum.LOGIN.value])
    def login(message):
        parts = message.text.split(" ")
        logger.debug("New logging attempt")
        if len(parts) < 2:
            msg = bot.send_message(
                message.chat.id,
                "Please, provide email to share the spreadsheets with it.",
            )
            bot.register_next_step_handler(msg, email_handler)
        else:
            message.text = parts[1]
            email_handler(message)

    logger.info("Initial commands registered")
