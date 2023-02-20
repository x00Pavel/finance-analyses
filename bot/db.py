import logging

from mongoengine import Document, StringField, ListField, connect

from bot.config import MongoConfig

logger = logging.getLogger(__name__)


def connect_db(config: MongoConfig):
    connection = connect(config.db, username=config.user, password=config.passwd.get_secret_value(), host=config.host,)
    logger.info(f'Connected to MongoDB: {connection}')


class User(Document):
    login = StringField(required=True, primary_key=True)
    personal_email = StringField(required=True)
    additional_emails = ListField(StringField(), required=False)
    categories = ListField(StringField(), required=False)

    def add_additional_email(self, email: list[str]):
        self.additional_emails.extend(email)
        return self.save()

    def add_category(self, category: str):
        self.categories = list(set(filter(None, category.split(' '))))
        logger.debug(f'Result categories: {self.categories}')
        return self.save()


def store_user(user_id, user_email) -> Document:
    return User(login=user_id, personal_email=user_email).save()


def get_user(user_id) -> User:
    logger.debug(f'Getting user by id: {user_id}')
    login = user_id.username or str(user_id.id)
    return User.objects(login=login).first()

