import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
import logging
import sys
import plotly.graph_objects as go


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

cur_dir = Path.cwd()
db_file = cur_dir / 'data.db'
data_dir = cur_dir / 'data'
data_dir.mkdir(exist_ok=True)
db_file.touch(exist_ok=True)
conn = create_engine(f'sqlite:///{db_file}')


@dataclass
class Category:
    name: str
    key_words: list[str] = field(default_factory=list)
    transaction: pd.Series = field(default_factory=lambda : pd.Series)
    bank_category: list[str] = field(default_factory=list)


def gen_categories() -> list[Category]:
    food = Category(
        name='Продукты',
        key_words=['Albert', 'Lidl', 'Kaufland', 'Billa', 'ASIAN MANGO', 'maso',
                'GLOBUS BRNO', 'Potraviny FOLKOVA'])
    food_out_side = Category(
        name='Еда на вынос',
        key_words=['VENTANA', 'MOTMOT', 'McDonalds', 'KFC', 'Burger King',
                'Restaurant', 'Restaurace', 'CHILLI TREE', 'KOFIBOX','SUSHIMIX',
                'Damejidlo', 'Pizza', 'NEEXISTUJE', 'KAFE', 'JIDELNI VUZ']
        )
    go_pay = Category(
        name='GoPay',
        key_words=['GoPay'])
    additional = Category(
        name='Сторонние покупки',
        key_words=['DATART', 'PlayStation', 'CESKA POSTA', 'CINEMA', 'KVETINY',
                'CELIO', 'PRIMARK', 'SB Olympia Brno Brno', 'Kino', 'ROSSMANN',
                'HULK GYM', 'HULK GYM', 'relaxin', 'TIGER', 'ZARA', 'H&M',
                ])
    regular_payments = Category(
        name='Регулярные платежи',
        key_words=['hetzner', 'SPOTIFY', 'NETFLIX', 'BARBER', 'BUBELINY', 'Vodafone'],
        bank_category=['Nájem'])
    transport = Category(
        name='Транспорт',
        key_words=['DPP', 'Flixbus', 'www.cd.cz', 'MPLA', 'EDALNICE', 'IDSJMK'],
        bank_category=['Doprava',]
    )
    transfers_n_cache = Category(
        name='Переводы и выдача наличных',
        key_words=['Výber', 'Výběr z bankomatu', 'Revolut', 'MMB2713',
                'VÝBĚR HOTOVOSTI'],
        bank_category=['Bankomat']
    )

    return [food, food_out_side, go_pay, additional, regular_payments, transport, transfers_n_cache]


def get_clean_df(file_path: Path) -> pd.DataFrame:
    logger.info('Getting df from %s', file_path)
    df = pd.read_csv(file_path, delimiter=';')
    columns_2_remove = ['Číslo protiúčtu', 'Banka protiúčtu', 'Název účtu příjemce',
        'Splatnost', 'Variabilní Symbol', 'Specifický Symbol',
        'Konstantní Symbol', 'Zpráva pro příjemce', 'Poznámka pro mě',
        'Název trvalého příkazu', 'Popis platby 2', 'IBAN']
    rename_columns = {
        'Částka': 'amount',
        'Měna': 'currency',
        'Odesláno': 'sent_date',
        'Číslo účtu': 'account_number',
        'Název kategorie': 'category',
        'Typ transakce': 'transaction_type',
        'Popis platby': 'description',
        'Bankovní reference': 'bank_reference',
    }
    if any(i in df.columns for i in columns_2_remove):
        df.drop(columns_2_remove, axis=1, inplace=True)
    if any(i in df.columns for i in rename_columns):
        df.rename(columns=rename_columns, inplace=True)
    df['sent_date'] = pd.to_datetime(df['sent_date'], format='%d.%m.%Y')
    return df


def save_df(df: pd.DataFrame, name: str = 'transactions', index=False, **kwargs) -> None:
    logger.debug('Saving df to db %s', name)
    if column := kwargs.pop('column_2_index', None):
        df.set_index(column, inplace=True)
    df['created_at'] = datetime.now()
    df.to_sql(name, conn, if_exists='append', index=index, **kwargs)


def process_df(df: pd.DataFrame) -> None:
    logger.debug('Processing df')
    common_categories = gen_categories()
    income = Category(name='Переводы на счет',)
    unsorted = Category(name='Неотсартированные')
    df['amount'] = df['amount'].str.replace(',', '.').astype({'amount': 'float64'}) 
    income.transaction = df[df['amount'] > 0].copy()
    df.drop(income.transaction.index, inplace=True)
    df.fillna('No value', inplace=True)

    for cat in common_categories:
        cat.transaction = df[df['description'].str.contains('|'.join(cat.key_words), flags=re.IGNORECASE, regex=True)].copy()
        df.drop(cat.transaction.index, inplace=True)
        values = df[df['category'].isin(cat.bank_category)].copy()
        df.drop(values.index, inplace=True)
        pd.concat([cat.transaction, values])
    unsorted.transaction = df
    return common_categories + [income, unsorted]


def group_transaction(categories: list[Category]) -> None:
    logger.debug('Grouping transactions')
    for category in categories:
        category.transaction = category.transaction.groupby('sent_date')['amount'].sum()
    

def plot_transactions(df: pd.DataFrame) -> None:
    df.sent_date = df.sent_date.dt.strftime('%Y-%m-%d')
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=df.columns, fill_color='paleturquoise', align='left'),
                cells=dict(values=df.transpose().values.tolist(),  fill_color='lavender', align='left')
            )
        ],
    )
    fig.show()


def group_df(categories: list[Category]) -> pd.DataFrame:
    grouped_df = pd.DataFrame(pd.date_range(start='2022-12-01', end='2022-12-31', freq='D'), columns=['sent_date'])
    for cat in categories:
        cat.transaction.name = cat.name
        grouped_df = pd.merge(grouped_df, cat.transaction, on='sent_date', how='outer')
    grouped_df.fillna(0, inplace=True)
    return grouped_df


def main():
    logger.info('Starting script')
    df = get_clean_df(data_dir / '12-2022-moneta.csv')
    save_df(df)
    processed_categories = process_df(df)
    group_transaction(processed_categories)
    grouped_df = group_df(processed_categories)
    save_df(grouped_df,
            name='grouped_transactions')
    plot_transactions(grouped_df)


if __name__ == '__main__':
    main()
