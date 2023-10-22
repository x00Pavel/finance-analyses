import logging

from mongoengine import Document, StringField, ListField, connect, FloatField

from bot.config import MongoConfig
from bot.datatypes import Expanses
from bot.storage.storage_base import Storage

logger = logging.getLogger(__name__)


def connect_db(config: MongoConfig):
    connection = connect(
        config.db,
        username=config.user,
        password=config.passwd.get_secret_value(),
        host=config.host,
    )
    logger.info(f"Connected to MongoDB: {connection}")


class User(Document):
    login = StringField(required=True, primary_key=True)
    personal_email = StringField(required=True)
    additional_emails = ListField(StringField(), required=False)
    categories = ListField(StringField(), required=False)

    def add_additional_email(self, email: list[str]):
        self.additional_emails.extend(email)
        return self.save()

    def add_category(self, category: str):
        self.categories = list(set(filter(None, category.split(" "))))
        logger.debug(f"Result categories: {self.categories}")
        return self.save()


class ExpansesDbStorage(Document, Storage):
    user_id: str = StringField(required=True)
    text: list[str] = ListField(StringField(), required=False, default=[])
    amount: float = FloatField(required=True)
    category = StringField(required=False)
    date = StringField(required=False)

    @classmethod
    def write_expanse(cls, expanses: Expanses):
        expanse_obj = cls(
            user_id=expanses.user.id,
            text=expanses.text,
            amount=expanses.amount,
            category=expanses.category,
            date=expanses.date.strftime("%Y-%m-%d"),
        )
        logger.debug(f"Saving expanses: {expanse_obj.to_json()}")
        return expanse_obj.save()


def store_user(user_id, user_email) -> Document:
    return User(login=user_id, personal_email=user_email).save()


def get_user(user_id) -> User:
    login = user_id.username or str(user_id.id)
    logger.debug(f"Getting user by login: {login}")
    return User.objects(login=login).first()
