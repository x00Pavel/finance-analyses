import logging
from datetime import datetime

from telebot import formatting
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot.datatypes import CommandsEnum, Expanses
from bot.db import get_user
from bot.exceptions import BotException
from bot.google import GoogleSheet
from bot.helpers import date_format, get_raw_message


logger = logging.getLogger(__name__)


def expanse_factory(text: str, user: "User", **kwargs) -> Expanses:
    parts = get_raw_message(text)
    amount = kwargs.get('amount', None)
    category = kwargs.get('category', None)
    date = kwargs.get('date', None)
    return Expanses(user=user,
                    text=parts,
                    amount=amount,
                    category=category,
                    date=date)


def get_month(text):
    parts = text.split(' ')
    return int(parts[1]) if len(parts) > 1 else datetime.now().month


def gen_categories_buttons(expanse: Expanses):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    post_fix = f'{expanse.date.strftime(date_format)}'
    post_fix += f' {expanse.amount}' if expanse.amount else ''
    markup.add(*[InlineKeyboardButton(text=category,
                                      callback_data=f"user_category {category} {post_fix}")
                 for category in expanse.user.categories])
    return markup


def register_gs_commands(bot, gs: GoogleSheet):
    @bot.message_handler(commands=[CommandsEnum.NEW.value])
    def new_sheet(message):
        month = get_month(message.text)
        user = get_user(message.from_user)
        try:
            if not user.personal_email:
                msg = f'Please, provide your email with /{CommandsEnum.LOGIN.value} ' \
                      'command to share the spreadsheet with it.'
                bot.send_message(message.chat.id, msg)
            else:
                logger.debug(f'Creating new sheet for {user.login} and month {month}')
                month = gs.create_sheet(user, month)
                bot.send_message(message.chat.id, f'New sheet created for {user.login} and month {month}')
        except BotException as e:
            bot.send_message(message.chat.id, e)

    def evaluate_expense(chat_id, expense: Expanses):
        if expense.category not in expense.user.categories:
            logger.debug(f'Category {expense.category} is not in {expense.user.categories}')
            text = f'Category {expense.category} is not in your list of categories. Please, choose one of them'
            bot.send_message(chat_id, text, reply_markup=gen_categories_buttons(expense))
        elif expense.amount is None:
            logger.debug(f'Amount is not provided')
            text = f'Amount is not provided. Please, provide it'
            msg = bot.send_message(chat_id, text)
            bot.register_next_step_handler(msg, amount_handler, expense)
        elif expense.date.month > datetime.today().month:
            raise BotException(f'Date is in the future {expense.date.strftime(date_format)}')
        else:
            logger.debug(f'Adding expense {expense}')
            gs.write_expanse(expense)
            bot.send_message(chat_id, f"Added {expense}")

    @bot.callback_query_handler(lambda call: call.data.startswith('user_category'))
    def category_button_handler(call):
        logger.debug(f'Category button handler: {call.data}')
        user = get_user(call.from_user)
        expense = expanse_factory(call.data, user)
        logger.debug(f'Expense: {expense}')
        evaluate_expense(call.message.chat.id, expense)

    def amount_handler(message, expense: Expanses):
        try:
            expense.amount = float(message.text)
            evaluate_expense(message.chat.id, expense)
        except ValueError:
            msg = bot.reply_to(message, f'Amount should be a number. Please, try again')
            bot.register_next_step_handler(msg, amount_handler, expense)

    @bot.message_handler(commands=[CommandsEnum.ADD.value])
    def add_expense(message):
        try:
            user = get_user(message.from_user)
            if not user:
                raise BotException(f'You are not logged in. Please, use /{CommandsEnum.LOGIN.value} for this')
            expanse = expanse_factory(message.text, user)
            evaluate_expense(message.chat.id, expanse)
        except BotException as e:
            logger.exception(e)
            bot.reply_to(message, e.msg + '\nPlease, try again')
        except Exception as e:
            bot.reply_to(message, f'Unexpected exception is raised: {formatting.mbold(e)}')

    logger.info('Google Sheets commands registered')
