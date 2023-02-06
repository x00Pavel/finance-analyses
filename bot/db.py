from mongoengine import Document, StringField, ListField, connect

url = "mongodb://root:root_pswd@127.0.0.1:27017"
connect('fin_bot', host=url)


class User(Document):
    login = StringField(required=True, primary_key=True)
    personal_email = StringField(required=True)
    additional_emails = ListField(StringField(), required=False)

    def add_additional_email(self, email: list[str]):
        self.additional_emails.extend(email)
        self.save()


def store_user(user_id, user_email) -> Document:
    return User(login=user_id, personal_email=user_email).save()


def get_user_creds(user_id) -> User:
    return User.objects(login=user_id).first()

