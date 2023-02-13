import dataclasses
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from mongoengine import Document

from bot.db import User
from bot.helpers import get_raw_message, date_format

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
    user: User
    text: list[str]
    date: datetime = None
    category: str = None
    amount: float = None

    def __post_init__(self):

        for i in self.text:
            logger.debug(f'Item: {i}')
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
        logger.debug(f'Expanses: {self}')

    def default(self):
        return dataclasses.asdict(self)

    def __str__(self):
        return f'{self.amount} to {self.category} at {self.date.strftime(date_format)}'


class CommandsEnum(Enum):
    LIST = "list_cmd"
    ADD_CATEGORY = 'add_category'
    START = 'start'
    LOGIN = 'login'
    NEW = 'new'
    ADD = 'add'
    HELP = 'help'
    ADD_EMAIL = 'add_email'
