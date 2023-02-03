from telebot import types


def get_raw_message(text: str) -> list[str]:
    return text.split(' ')[1:]


def gen_yes_no_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("Yes", callback_data="cb_yes"),
                 types.InlineKeyboardButton("No", callback_data="cb_no"))
    return keyboard
