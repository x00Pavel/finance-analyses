import logging

from bot.commands import categories, emails, initial, gs_commands

logger = logging.getLogger(__name__)


def register_commands(bot, gs):
    initial.register_initial_commands(bot)
    categories.register_categories_commands(bot)
    emails.register_emails_commands(bot)
    gs_commands.register_gs_commands(bot, gs)

    logger.info('All commands registered')
