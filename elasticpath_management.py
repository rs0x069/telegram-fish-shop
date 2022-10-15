import os

import requests

from time import time

token = None
token_expires = None


def get_token():
    global token
    global token_expires

    client_id = os.getenv('ELASTICPATH_CLIENT_ID')
    client_secret = os.getenv('ELASTICPATH_CLIENT_SECRET')

    url = 'https://api.moltin.com/oauth/access_token'

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    timestamp_current = time()

    if not token or timestamp_current > token_expires:
        response = requests.post(url=url, data=data)
        response.raise_for_status()
        response_encoded = response.json()
        token = response_encoded["access_token"]
        token_expires = response_encoded["expires"]


def get_all_products():
    get_token()

    url = 'https://api.moltin.com/pcm/products'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    products = requests.get(url=url, headers=headers)
    products.raise_for_status()

    return products.json()


def get_product(product_id):
    get_token()

    url = f'https://api.moltin.com/pcm/products/{product_id}'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    product = requests.get(url=url, headers=headers)
    product.raise_for_status()

    return product.json()


def get_product_files(product_id):
    get_token()

    url = f'https://api.moltin.com/pcm/products/{product_id}/relationships/files'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    product_files = requests.get(url=url, headers=headers)
    product_files.raise_for_status()

    return product_files.json()


def get_file_by_id(file_id):
    get_token()

    url = f'https://api.moltin.com/v2/files/{file_id}'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    file = requests.get(url=url, headers=headers)
    file.raise_for_status()

    return file.json()


def create_customer(name, email):
    get_token()

    url = f'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
        }
    }

    customer = requests.post(url=url, headers=headers, json=data)
    customer.raise_for_status()

    return customer.json()


def get_customer(customer_id):
    get_token()

    url = f'https://api.moltin.com/v2/customers/{customer_id}'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    customer = requests.get(url=url, headers=headers)
    customer.raise_for_status()

    return customer.json()


def create_custom_cart(name, cart_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    data = {
        'data': {
            'name': name,
            'id': cart_id,
        }
    }

    custom_cart = requests.post(url=url, headers=headers, json=data)
    custom_cart.raise_for_status()

    return custom_cart.json()


def get_custom_cart(cart_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    custom_cart = requests.get(url=url, headers=headers)
    custom_cart.raise_for_status()

    return custom_cart.json()


def create_customer_cart_association(cart_id, customer_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}/relationships/customers'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    data = {
        'data': [{
            'type': 'customer',
            'id': customer_id
        }]
    }

    customer_cart_association = requests.post(url=url, headers=headers, json=data)
    customer_cart_association.raise_for_status()

    if customer_cart_association.status_code == 204:
        return 'The customer has already been associated to the cart'

    return customer_cart_association.json()


def get_cart(cart_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    cart = requests.get(url=url, headers=headers)
    cart.raise_for_status()

    return cart.json()


def get_latest_release_of_catalog(catalog_id):
    get_token()

    url = f'https://api.moltin.com/pcm/catalogs/{catalog_id}/releases/latest'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    latest_release = requests.get(url=url, headers=headers)
    latest_release.raise_for_status()

    return latest_release.json()


def get_cart_items(cart_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    cart_items = requests.get(url=url, headers=headers)
    cart_items.raise_for_status()

    return cart_items.json()


def add_product_to_cart(cart_id, product_id, quantity):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity,
        }
    }

    cart = requests.post(url=url, headers=headers, json=data)
    cart.raise_for_status()

    return cart.json()


def remove_cart_item(cart_id, cart_item_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}/items/{cart_item_id}'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    cart = requests.delete(url=url, headers=headers)
    cart.raise_for_status()

    return cart.json()


def delete_cart(cart_id):
    get_token()

    url = f'https://api.moltin.com/v2/carts/{cart_id}'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    cart = requests.delete(url=url, headers=headers)
    cart.raise_for_status()

    return cart
