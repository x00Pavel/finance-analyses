from bot.tg import bot

from dotenv import load_dotenv
load_dotenv("/.env")

def main():
    bot.polling()
