import logging

from bot.commands import categories, emails, initial, storage_commands
from bot.storage.storage_base import Storage

logger = logging.getLogger(__name__)


def register_commands(bot, storage: Storage) -> None:
    initial.register_initial_commands(bot)
    categories.register_categories_commands(bot)
    emails.register_emails_commands(bot)
    storage_commands.register_storage_commands(bot, storage)

    logger.info("All commands registered")
