import requests
import config

def get_orders():
    r = requests.get(config.API_ORDERS)
    r.raise_for_status()
    return r.json()

def get_order_details(order_id):
    r = requests.get(config.API_ORDER_DETAILS(order_id))
    r.raise_for_status()
    return r.json()

def mark_detail_done(detail_id):
    r = requests.post(config.API_MARK_DONE(detail_id))
    r.raise_for_status()
    return r.json()
