
import csv

ORDERS_BOOK_FPATH = "data/orders_book.csv"


def load_orders_book(fpath: str = ORDERS_BOOK_FPATH) -> list[dict]:
    """Loads orders data into a list of dicts"""
    data = []
    with open(fpath, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for row in csv_reader:
            if row.get('paid'):
                row['paid'] = float(row['paid'])
            data.append(row)
    return data
