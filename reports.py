
import math

import csfloat
import file_utils


def report_returns(orders_data: list[dict], prices_data: list[dict], price_ref: str = 'buy_price'):
    """Calculates metrics on potential returns over orders book"""
    results = []
    for buy in orders_data:
        current_info = [i for i in prices_data if i['name'] == buy['name']][0]
        my_sell_price = math.floor(current_info[price_ref] * 100 * (1 - csfloat.CSF_SELL_FEE)) / 100
        doc = {
            'paid_price': buy['paid_price'],
            'profit': int(my_sell_price > buy['paid_price']),
            'rev': my_sell_price
        }
        results.append(doc)
    print(f'transactions: {len(results)}')
    profitable_perc = round(sum([i ['profit'] for i in results]) / len(results) * 100)
    print(f'profitable:   {profitable_perc}%')
    spent = sum([i['paid_price'] for i in results])
    print(f'total spent:  {spent}')
    rev = sum([i['rev'] for i in results])
    print(f'total rev:    {rev}')
    roi = round(rev / spent * 100)
    print(f'roi:          {roi}%')


def print_orders_book_roi_report():
    """Prints ROI report on orders book"""
    my_orders = file_utils.load_csv_data(file_utils.ORDERS_BOOK_FPATH)
    current_prices_data = csfloat.gather_current_prices(my_orders)
    report_returns(my_orders, current_prices_data)
