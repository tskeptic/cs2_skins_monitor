

import os
import time
import requests
import datetime
import dotenv
import tqdm
import requests_cache

dotenv.load_dotenv()

requests_cache.install_cache(
    'cache_csf',
    expire_after=60*60*4,
    allowable_codes=(200,),
    allowable_methods=('GET', 'POST'),
    ignored_parameters=('Authorization'),
    stale_if_error=False,
    )

CSFLOAT_BASE_URL = "https://csfloat.com/api/v1"
HEADERS = {'Authorization': os.getenv("CSFLOAT_API_KEY")}
CSF_SELL_FEE = 0.021  # 0.1% extra just to be sure
GLOBAL_POST_REQUEST_SLEEP = 1.3


def get_listings(skin_name: str, qty: int = 5) -> list[dict]:
    """Obtain current selling listings for the item"""
    payload = {'limit': qty, 'sort_by': 'lowest_price', 'type': 'buy_now', 'market_hash_name': skin_name}
    req = requests.get(f'{CSFLOAT_BASE_URL}/listings', headers=HEADERS, params=payload)
    req.raise_for_status()
    if not req.from_cache:
        time.sleep(GLOBAL_POST_REQUEST_SLEEP)
    result = req.json()['data']
    if len(result) < 1:
        print(f'Warning: No listings found for "{skin_name}"')
    return result


def get_buy_orders(listing: dict, qty: int = 10) -> list[dict]:
    """Obtains current buy orders for the listing"""
    listing_id = listing.get('id')
    payload = {'limit': qty}
    req = requests.get(f'{CSFLOAT_BASE_URL}/listings/{listing_id}/buy-orders', headers=HEADERS, params=payload)
    req.raise_for_status()
    if not req.from_cache:
        time.sleep(GLOBAL_POST_REQUEST_SLEEP)
    result = req.json()
    if len(result) < 1:
        print(f'Warning: No buy orders found for listing id "{listing_id}"')
    return result


def get_sales_graph(skin_name: str) -> list[dict]:
    """Obtains historical data of avg/median sale price"""
    req = requests.get(f'{CSFLOAT_BASE_URL}/history/{skin_name}/graph', headers=HEADERS)
    req.raise_for_status()
    if not req.from_cache:
        time.sleep(GLOBAL_POST_REQUEST_SLEEP)
    result = req.json()
    if len(result) < 1:
        print(f'Warning: No sales history found for "{skin_name}"')
    return result


def gather_current_prices(orders_data: list[dict]) -> list[dict]:
    """Collects current info of prices for each item from csfloat"""
    min_buy_orders_qty = 2
    history_period = 3
    current_prices_data = []
    # obtaining list of unique names to avoid duplicated requests
    unique_names = {i['name'] for i in orders_data}
    # iterating over skins
    for skin in tqdm.tqdm(unique_names, ncols=99):
        listings = get_listings(skin)
        lowest_sell_price = listings[0]['price'] / 100
        estimated_price = listings[0]['reference'].get('predicted_price', listings[0]['reference'].get('base_price')) / 100
        buy_orders = get_buy_orders(listings[0])
        chosen_buy_order = next((b for b in buy_orders if b['qty'] >= min_buy_orders_qty), buy_orders[2 if len(buy_orders) >= 3 else -1])
        max_buy_order_price = chosen_buy_order['price'] / 100
        sales_history = get_sales_graph(skin)[:history_period]
        avg_history_sold_count = int(sum([i['count'] for i in sales_history]) / history_period)
        avg_history_sold_price = round(sum([i['avg_price'] for i in sales_history]) / history_period / 100, 2)
        doc = {
            'fetch_date': str(datetime.datetime.now().date()),
            'name': skin,
            'sell_price': lowest_sell_price,
            'estimated_price': estimated_price,
            'buy_price': max_buy_order_price,
            'sell_history_avg_qty': avg_history_sold_count,
            'sell_history_avg_price': avg_history_sold_price
        }
        current_prices_data.append(doc)
    return current_prices_data
