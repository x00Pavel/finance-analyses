from mongoengine import Document, StringField, ListField, connect

from bot.config import MongoConfig


def connect_db(config: MongoConfig):
    url = f"mongodb://{config.user}:{config.passwd.get_secret_value()}@{config.host}:{config.port}"
    connect(config.db, host=url)


class User(Document):
    login = StringField(required=True, primary_key=True)
    personal_email = StringField(required=True)
    additional_emails = ListField(StringField(), required=False)
    categories = ListField(StringField(), required=False)

    def add_additional_email(self, email: list[str]):
        self.additional_emails.extend(email)
        return self.save()

    def add_category(self, category: str):
        self.categories.extend(category.split(' '))
        return self.save()


def store_user(user_id, user_email) -> Document:
    return User(login=user_id, personal_email=user_email).save()


def get_user(user_id) -> User:
    login = user_id.username or str(user_id.id)
    return User.objects(login=login).first()

