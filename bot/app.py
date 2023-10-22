import logging

import flask
from flask import Flask, request
from telebot.types import Update

from bot.config import Config
from bot.storage.db import connect_db, ExpansesDbStorage
from bot.tg import init_bot

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    config = Config()
    connect_db(config.mongo)

    # storage = GoogleSheet(config.gs) if config.gs else ExpansesDbStorage()
    storage = ExpansesDbStorage()
    bot = init_bot(config.tg, storage)
    logger.info("Bot is ready to work.")

    @app.route("/")
    def index():
        if bot.get_webhook_info().url == "":
            return flask.redirect(f"/set_webhook/{bot.token}")
        return "OK"

    @app.route(f"/{bot.token}", methods=["POST"])
    def webhook():
        logger.debug("Received update: %s", request.json)
        update = Update.de_json(request.json)
        bot.process_new_updates([update])
        return "OK"

    @app.route(f"/set_webhook/{bot.token}", methods=["GET"])
    def set_webhook():
        if bot.get_webhook_info().url == "":
            url = request.url_root + bot.token
            if not url.startswith("http://"):
                url = "https://" + url
            elif url.startswith("http://"):
                url = url.replace("http://", "https://")
            logger.info(f"Webhook url: {url}")
            try:
                s = bot.set_webhook(url=url)
            except Exception as e:
                logger.error(e)
                return e
            else:
                if s:
                    return "webhook setup ok"
                else:
                    return "webhook setup failed"
        else:
            return "webhook already setup"

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8080, debug=True)
