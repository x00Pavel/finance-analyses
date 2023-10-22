import dataclasses
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from mongoengine import Document
from telebot.types import BotCommand

from bot.helpers import date_format

logger = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, Document):
            return o.to_json()
        if isinstance(o, datetime):
            return o.strftime(date_format)
        return super().default(o)


@dataclass
class Expanses:
    user: "User"
    text: list[str]
    date: datetime = None
    category: str = None
    amount: float = None

    def __post_init__(self):
        for i in self.text:
            logger.debug(f"Item: {i}")
            if not self.category:
                if i in self.user.categories:
                    self.category = i
                    continue
            if not self.amount:
                try:
                    self.amount = float(i)
                    continue
                except ValueError:
                    pass
            if not self.date:
                try:
                    self.date = datetime.strptime(i, date_format)
                except ValueError:
                    pass

        if self.date is None:
            self.date = datetime.today()
        logger.debug(f"Expanses: {self}")

    def default(self):
        return dataclasses.asdict(self)

    def __str__(self):
        return f"{self.amount} to {self.category} at {self.date.strftime(date_format)}"


class CommandsEnum(Enum):
    LIST = "list_cmd"
    ADD_CATEGORY = "set_categories"
    START = "start"
    LOGIN = "login"
    NEW = "new"
    ADD = "add"
    HELP = "help"
    ADD_EMAIL = "add_email"


commands_description = [
    BotCommand(command=CommandsEnum.START.value, description="Start bot"),
    BotCommand(
        command=CommandsEnum.LIST.value, description="List of available commands"
    ),
    BotCommand(
        command=CommandsEnum.ADD_CATEGORY.value, description="Add category to your list"
    ),
    BotCommand(
        command=CommandsEnum.LOGIN.value,
        description="Add email to share the spreadsheets with it",
    ),
    BotCommand(command=CommandsEnum.NEW.value, description="Create new spreadsheet"),
    BotCommand(
        command=CommandsEnum.ADD.value,
        description="Add new expanses to the spreadsheet. "
        "You can specify all values to the command, or bot will ask you for them. "
        "Values should be separated by space and passed in any order. "
        "For example: /add 100 food 2021-01-01 or /add 100",
    ),
    BotCommand(command=CommandsEnum.HELP.value, description="Help"),
    BotCommand(
        command=CommandsEnum.ADD_EMAIL.value,
        description="Add email to share the spreadsheets with it",
    ),
]
