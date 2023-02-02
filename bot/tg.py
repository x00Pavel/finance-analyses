import telebot
from os import environ

from bot.google import GoogleSheet


bot = telebot.TeleBot(environ.get('TG_API_TOKEN'))
gs = GoogleSheet()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")
    # Ask for email to share new documents with
    # Store email in db if not already stored

def get_month(text):
    parts = text.split(' ')
    return int(parts[1]) if len(parts) > 1 else None


@bot.message_handler(commands=['new'])
def new_sheet(message):
    month = get_month(message.text)
    gs.create_sheet(month)


def create_new_doc(message):
    # Create new doc
    # Share doc with user email
    # Send doc link to user
    pass
