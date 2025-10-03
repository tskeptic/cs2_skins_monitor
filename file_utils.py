
import csv

NUMERICAL_FIELDS = {'paid_price', 'probability'}
ORDERS_BOOK_FPATH = "data/orders_book.csv"


def load_csv_data(fpath: str) -> list[dict]:
    """Loads csv data into a list of dicts"""
    data = []
    with open(fpath, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for row in csv_reader:
            for num_col in NUMERICAL_FIELDS:
                if row.get(num_col):
                    row[num_col] = float(row[num_col])
            data.append(row)
    return data
