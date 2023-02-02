import logging
from os import environ
import gspread
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


categories = {'food': 'B1', 'restaurants': 'C1', 'entertainment': 'D1'}


class GoogleSheet:
    gs_file = environ.get('GS_FILE')
    
    def __init__(self):
        self.gc = gspread.service_account(filename=self.gs_file)


    def write_to_sheet(self, file, cell, data, worksheet=None):
        ...

    def _get_dates(self, month: int):
        year = datetime.now().year
        start_date = date(year, month, 1) 
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        delta = end_date - start_date
        return [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    def get_sheet(self, file, month: int):
        try:
            return file.worksheet(f"{month}")
        except gspread.exceptions.WorksheetNotFound:
            logger.info(f'Creating sheet for {month}')
            return file.add_worksheet(title=f'{month}', rows=45, cols=10)
    
    def get_file(self, year: int):
        try:
            file = self.gc.open(f'{year}')
        except gspread.exceptions.SpreadsheetNotFound:
            logger.info(f'Creating file for {year}')
            file = self.gc.create(f'{year}')
        return file
    
    def create_sheet(self, month: int = None):
        date_now = datetime.now()
        date_year = date_now.year
        if month is None:
            month = date_now.month
        dates_list = self._get_dates(month)
        file = self.get_file(date_year)
        ws = self.get_sheet(file, month)
        num_of_columns = 1 + len(categories)
        my_list = [[None for _ in range(num_of_columns)] for _ in range(len(dates_list) + 1)]
        my_list[0] = ['Date', *categories.keys()]
        for i, date_ in enumerate(dates_list, 1):
            my_list[i][0] = date_.strftime('%d.%m.%Y')
        last_column = chr(ord('A') + num_of_columns)
        last_row = len(dates_list) + 1
        cell_range =f'A1:{last_column}{last_row}'
        
        ws.update(cell_range, my_list)
        
        # ws.values_update(
            
        #     params={'valueInputOption': 'RAW'}, 
        #     body={'values': my_list}
        # )
        
        # ws.update_cells('A1', [[date.strftime('%d.%m.%Y') for date in dates_list]])    

