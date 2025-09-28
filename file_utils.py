
import csv

ORDERS_BOOK_FPATH = "data/orders_book.csv"


def load_csv_data(fpath: str) -> list[dict]:
    """Loads csv data into a list of dicts"""
    data = []
    with open(fpath, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for row in csv_reader:
            if row.get('paid_price'):
                row['paid_price'] = float(row['paid_price'])
            data.append(row)
    return data
