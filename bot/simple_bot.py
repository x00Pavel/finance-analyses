from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Column,
    Float,
    Date,
    Boolean,
    create_engine,
    insert,
)
from telebot import TeleBot
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
TOKEN = "5555462952:AAGhLhkWAQCEkGoXvYS47O6c4gSIBDk3iWE"
bot = TeleBot(TOKEN)
engine = create_engine("sqlite:///database.db")


class Expanse(Base):
    __tablename__ = "cash_flow"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    amount = Column(Float)
    category = Column(String)
    date = Column(Date)
    income = Column(Boolean)


@bot.message_handler(commands=["add"])
def add_to_db(message):
    flow = Expanse(
        user_id=message.from_user.id,
        amount=100,
        category="food",
        date=datetime.today().date(),
        income=False,
    )
    with Session(engine) as s:
        s.add(flow)
        s.commit()
    bot.send_message(message.chat.id, "Insert to db")


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Hello, World!")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def main():
    Expanse.metadata.create_all(engine)
    # Create a table with the appropriate Columns
    bot.remove_webhook()
    bot.infinity_polling()


if __name__ == "__main__":
    main()
