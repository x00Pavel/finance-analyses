import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bot.db import User
from bot.exceptions import BotException
from bot.helpers import get_raw_message, date_format

logger = logging.getLogger(__name__)


@dataclass
class Expanses:
    user: User
    full_message: str
    text: list[str] = None
    date: datetime = datetime.today()
    category: str = None
    amount: float = None

    def __post_init__(self):
        self.text = get_raw_message(self.full_message)
        logger.debug(f'Categories: {self.user.categories}')
        logger.debug(f'Text: {self.text}')
        for i in self.text:
            logger.debug(f'Checking {i}')
            if i in self.user.categories:
                self.category = i
                continue
            try:
                self.amount = float(i)
                continue
            except ValueError:
                pass
            try:
                self.date = datetime.strptime(i, date_format)
            except ValueError:
                pass
        logger.debug(f'Expanses: {self}')
        if self.category is None:
            raise BotException(f'Category not found. Available categories: {", ".join(self.user.categories)}',
                               self.full_message)
        if self.amount is None:
            raise BotException('Amount not found',
                               self.full_message)

    def __str__(self):
        return f'{self.category} {self.amount} at {self.date.strftime(date_format)}'


class CommandsEnum(Enum):
    ADD_CATEGORY = 'add_category'
    START = 'start'
    LOGIN = 'login'
    NEW = 'new'
    ADD = 'add'
    HELP = 'help'
    ADD_EMAIL = 'add_email'
