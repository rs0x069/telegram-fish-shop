import os

from dotenv import load_dotenv

from elasticpath_management import *


def main():
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    elasticpath_client_id = os.getenv('ELASTICPATH_CLIENT_ID')
    elasticpath_client_secret = os.getenv('ELASTICPATH_CLIENT_SECRET')

    token = get_token(elasticpath_client_id, elasticpath_client_secret)
    print(f'{token=}')

    products = get_all_products(token)
    first_product_id = products['data'][1]['id']
    print(f'{products=}')
    print(f'{first_product_id=}')

    # customer = create_customer(token, name='Ivan', email='ivan@localhost.com')
    # print(customer)

    # custom_cart = create_custom_cart(token, name="Ivan's cart", cart_id="ivan_telegram_id")
    # print(f'{custom_cart=}')

    cart_id = get_cart(token, cart_id='ivan_telegram_id')['data']['id']
    print(f'{cart_id=}')

    # customer_cart_association = create_customer_cart_association(
    #     token,
    #     cart_id=cart_id,
    #     customer_id='f8b8e91c-a346-404a-9aef-24838b0ea4da'
    # )
    # print(f'{customer_cart_association=}')

    # print(add_product_to_cart(token, cart_id, f'{first_product_id}'))

    cart_items = get_cart_items(token, cart_id)
    print(f'{cart_items=}')

    # latest_release_of_catalog = get_latest_release_of_catalog(token, catalog_id='7ea1fbee-7653-40b6-8d16-2575db42c508')
    # print(f'{latest_release_of_catalog=}')


if __name__ == '__main__':
    main()
