import requests


def get_token(client_id, client_secret):
    url = 'https://api.moltin.com/oauth/access_token'

    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.post(url=url, data=data)
    # response.raise_for_status()
    json_response = response.json()
    token = json_response["access_token"]

    return token


def get_all_products(token):
    url = 'https://api.moltin.com/pcm/products'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    products = requests.get(url=url, headers=headers)
    # products.raise_for_status()

    return products.json()


def get_product(token, product_id):
    url = f'https://api.moltin.com/pcm/products/{product_id}'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    product = requests.get(url=url, headers=headers)
    # product.raise_for_status()

    return product.json()


def create_customer(token, name, email):
    url = f'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
            # 'password': 'mysecretpassword'
        }
    }

    customer = requests.post(url=url, headers=headers, json=data)
    # customer.raise_for_status()

    return customer.json()


def create_custom_cart(token, name, cart_id):
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
    # custom_cart.raise_for_status()

    return custom_cart.json()


def create_customer_cart_association(token, cart_id, customer_id):
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
    # customer_cart_association.raise_for_status()

    if customer_cart_association.status_code == 204:
        return 'The customer has already been associated to the cart'

    return customer_cart_association.json()


def get_cart(token, cart_id):
    url = f'https://api.moltin.com/v2/carts/{cart_id}'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    cart = requests.get(url=url, headers=headers)
    # cart.raise_for_status()

    return cart.json()


def get_latest_release_of_catalog(token, catalog_id):
    url = f'https://api.moltin.com/pcm/catalogs/{catalog_id}/releases/latest'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    latest_release = requests.get(url=url, headers=headers)
    # latest_release.raise_for_status()

    return latest_release.json()


def get_cart_items(token, cart_id):
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'
    headers = {
        'Authorization': f'Bearer {token}',
    }

    cart_items = requests.get(url=url, headers=headers)
    # cart_items.raise_for_status()

    return cart_items.json()


def add_product_to_cart(token, cart_id, product_id):
    url = f'https://api.moltin.com/v2/carts/{cart_id}/items'

    headers = {
        'Authorization': f'Bearer {token}',
    }

    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': 1,
        }
    }

    product = requests.post(url=url, headers=headers, json=data)
    # product.raise_for_status()

    return product.json()
