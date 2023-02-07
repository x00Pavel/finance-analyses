import logging

from bot.datatypes import CommandsEnum
from bot.db import User, get_user

logger = logging.getLogger(__name__)


def register_categories_commands(bot):
    @bot.message_handler(commands=[CommandsEnum.ADD_CATEGORY.value])
    def add_category(message):
        parts = message.text.split(' ', 1)
        if len(parts) != 2:
            logger.debug('No category provided')
            msg = bot.send_message(message.chat.id, 'Please, provide(s) category name.')
            bot.register_next_step_handler(msg, category_handler)
        else:
            logger.info(f'New category for user %s: %s', message.from_user.username, parts[1])
            message.text = parts[1]
            category_handler(message)

    def category_handler(message):
        category = message.text
        logger.debug('Setting new categories')
        result = get_user(message.from_user.username).add_category(category)
        msg = f'Categories are set to {result.categories}'
        logger.debug('Sending message: %s', msg)
        bot.send_message(message.chat.id, msg)

    logger.info('Categories commands registered')
