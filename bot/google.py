import logging
from datetime import date, datetime, timedelta
from calendar import month_name
import gspread

from bot.config import GSConfig
from bot.datatypes import CommandsEnum
from bot.db import get_user, User
from bot.exceptions import BotException

logger = logging.getLogger(__name__)

prefix = 'Expenses'


class GoogleSheet:
    def __init__(self, cfg: GSConfig):
        self.gs = gspread.service_account(filename=cfg.creds)
        self.file_prefix = cfg.file_prefix

    @staticmethod
    def _get_dates(month: int):
        year = datetime.now().year
        start_date = date(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        delta = end_date - start_date
        return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

    @staticmethod
    def get_sheet(file, month: int):
        try:
            month = month_name[month]
            return file.worksheet(f"{month}")
        except gspread.exceptions.WorksheetNotFound:
            logger.info(f'Creating sheet for {month}')
            return file.add_worksheet(title=f'{month}', rows=45, cols=10)

    def get_file(self, user: User, year: int):
        file_name = f'{self.file_prefix} {user.login} {year}'
        try:
            file = self.gs.open(file_name)
        except gspread.exceptions.SpreadsheetNotFound:
            logger.info(f'Creating file {file_name}')
            file = self.gs.create(file_name)
            file.share(user.personal_email, perm_type='user', role='writer')
            logger.info(f'Sharing file with {user.personal_email} for {file_name}')

        return file

    def create_sheet(self, user: User, month: int = None):
        date_year = datetime.now().year
        if not user.categories:
            raise BotException(f'Please, provide categories with /{CommandsEnum.ADD_CATEGORY.value} command')
        dates_list = self._get_dates(month)
        file = self.get_file(user, date_year)
        ws = self.get_sheet(file, month)

        num_of_columns = 1 + len(user.categories)
        my_list = [['=0' for _ in range(num_of_columns)] for _ in range(len(dates_list) + 1)]
        my_list[0] = ['Date', *user.categories]
        for i, date_ in enumerate(dates_list, 1):
            my_list[i][0] = date_.strftime('%d.%m.%Y')
        last_column = chr(ord('A') + num_of_columns)
        last_row = len(dates_list) + 1
        cell_range = f'A1:{last_column}{last_row}'
        ws.update(cell_range, my_list, raw=False)
        return month_name[month]

    def write_expanse(self, expanse: "Expanses"):
        if expanse.user is None:
            return 'User not found in database'
        if not expanse.user.categories:
            return f'No categories found for user {expanse.user}. ' \
                   f'Please add categories with /{CommandsEnum.ADD_CATEGORY.value} command'
        if expanse.category not in expanse.user.categories:
            return f'Category {expanse.category} not found for user {expanse.user}. ' \
                   f'Please add categories with /{CommandsEnum.ADD_CATEGORY.value} command'

        file = self.get_file(expanse.user, expanse.date.year)
        ws = self.get_sheet(file, expanse.date.month)
        date_row = ws.find(expanse.date.strftime('%d.%m.%Y'))
        category_column = ws.find(expanse.category)
        cell = ws.cell(date_row.row, category_column.col)
        logger.info(f'Writing {expanse} to {ws.title} at {cell.address}')
        ws.update(cell.address, f"={cell.value}+{expanse.amount}", raw=False)
