import os

import redis

from functools import partial

import telegram.parsemode
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Filters, CallbackQueryHandler, CommandHandler, MessageHandler

from elasticpath_management import *

_database = None


def show_menu(update, context, elasticpath_token):
    tg_user_id = update.effective_chat.id

    products = get_all_products(elasticpath_token)
    keyboard_buttons = []
    for product in products['data']:
        keyboard_buttons.append(
            [
                InlineKeyboardButton(text=product['attributes']['name'], callback_data=product['id'])
            ]
        )
    keyboard_buttons.append([InlineKeyboardButton(text='Корзина', callback_data=str(tg_user_id))])

    reply_markup = InlineKeyboardMarkup(keyboard_buttons)
    menu = context.bot.send_message(
        chat_id=tg_user_id,
        text='Выберите товар:',
        reply_markup=reply_markup
    )

    return menu


def show_description_with_image(update, context, elasticpath_token, query_data):
    tg_user_id = update.effective_chat.id

    product = get_product(elasticpath_token, query_data)
    product_id = product['data']['id']
    product_description = product['data']['attributes']['description']

    product_files = get_product_files(elasticpath_token, product_id)

    product_files_ids = product_files['data'][0]['id']

    file = get_file_by_id(elasticpath_token, product_files_ids)
    file_url = file['data']['link']['href']

    keyboard = [
        [
            InlineKeyboardButton('1 кг', callback_data=f'{product_id}_1'),
            InlineKeyboardButton('5 кг', callback_data=f'{product_id}_5'),
            InlineKeyboardButton('10 кг', callback_data=f'{product_id}_10'),
        ],
        [InlineKeyboardButton('Корзина', callback_data=str(tg_user_id))],
        [InlineKeyboardButton('Меню', callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    description = context.bot.send_photo(
        chat_id=tg_user_id,
        photo=file_url,
        caption=product_description,
        reply_markup=reply_markup
    )

    return description


def show_cart(update, context, elasticpath_token, tg_user_id):
    print('show_cart')
    cart_items = get_cart_items(elasticpath_token, tg_user_id)

    cart = 'Корзина:\n\n'
    for cart_item in cart_items['data']:
        product_quantity = cart_item['quantity']
        product_per_cost = cart_item['unit_price']['amount']
        product_amount = cart_item['value']['amount']

        cart += f"{cart_item['name']}\n" \
                f"{cart_item['description']}\n" \
                f"${product_per_cost} per kg\n" \
                f"{product_quantity}kg in cart for ${product_amount}\n" \
                f"\n"

    cart_amount = cart_items['meta']['display_price']['with_tax']['amount']
    cart += f'Total: ${cart_amount}'

    keyboard = []
    for cart_item in cart_items['data']:
        keyboard.append(
            [
                InlineKeyboardButton(text=f"Удалить из корзины: {cart_item['name']}", callback_data=cart_item['id'])
            ]
        )
    keyboard.append([InlineKeyboardButton('Меню', callback_data='menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    cart = context.bot.send_message(
        chat_id=tg_user_id,
        text=cart,
        reply_markup=reply_markup
    )

    return cart


def start(update, context, elasticpath_token):
    print('start')
    show_menu(update, context, elasticpath_token)
    return 'HANDLE_MENU'


def handle_menu(update, context, elasticpath_token):
    print('handle_menu')

    query = update.callback_query
    query.answer()

    tg_user_id = update.effective_user.id

    if query.data == str(tg_user_id):
        show_cart(update, context, elasticpath_token, tg_user_id)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return 'HANDLE_CART'

    show_description_with_image(update, context, elasticpath_token, query.data)
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(update, context, elasticpath_token):
    print('handle_description')

    query = update.callback_query
    query.answer()
    print(f"Selected option: {query.data}")

    tg_user_id = update.effective_user.id

    if query.data == 'menu':
        show_menu(update, context, elasticpath_token)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return 'HANDLE_MENU'

    if query.data == str(tg_user_id):
        show_cart(update, context, elasticpath_token, tg_user_id)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return 'HANDLE_CART'

    product_id = query.data.split('_')[0]
    product_quantity = query.data.split('_')[1]

    add_product_to_cart(elasticpath_token, tg_user_id, product_id, int(product_quantity))
    cart_items = get_cart_items(elasticpath_token, tg_user_id)

    return 'HANDLE_DESCRIPTION'


def handle_cart(update, context, elasticpath_token):
    print('handle_cart')

    query = update.callback_query
    query.answer()

    tg_user_id = update.effective_user.id

    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)

    if query.data == 'menu':
        show_menu(update, context, elasticpath_token)
        return 'HANDLE_MENU'

    remove_cart_item(elasticpath_token, tg_user_id, query.data)
    show_cart(update, context, elasticpath_token, tg_user_id)

    return 'HANDLE_CART'


def handle_users_reply(update, context, elasticpath_token):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    print(f'{user_reply=}')

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)
    print(f'{user_state=}')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
    }
    print(f'{states_functions=}')

    state_handler = states_functions[user_state]
    print(f'{state_handler=}')

    try:
        next_state = state_handler(update, context, elasticpath_token)
        db.set(chat_id, next_state)
    except Exception as err:
        print(f'Exception: {err}')


def get_database_connection():
    global _database
    if _database is None:
        database_username = os.getenv("DATABASE_USERNAME")
        database_password = os.getenv("DATABASE_PASSWORD")
        database_host = os.getenv("DATABASE_HOST")
        database_port = os.getenv("DATABASE_PORT")
        _database = redis.Redis(
            host=database_host,
            port=int(database_port),
            db=0,
            username=database_username,
            password=database_password,
            decode_responses=True
        )
    return _database


def main():
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    elasticpath_client_id = os.getenv('ELASTICPATH_CLIENT_ID')
    elasticpath_client_secret = os.getenv('ELASTICPATH_CLIENT_SECRET')
    elasticpath_token = get_token(elasticpath_client_id, elasticpath_client_secret)

    handle_users_reply_with_token = partial(handle_users_reply, elasticpath_token=elasticpath_token)

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply_with_token))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply_with_token))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply_with_token))

    # start_ep_token = partial(start, elasticpath_token=elasticpath_token)
    # updater.dispatcher.add_handler(CommandHandler('start', start_ep_token))
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

    # # customer = create_customer(token, name='Ivan', email='ivan@localhost.com')
    # # print(customer)
    #
    # # custom_cart = create_custom_cart(token, name="Ivan's cart", cart_id="ivan_telegram_id")
    # # print(f'{custom_cart=}')
    #
    # cart_id = get_cart(token, cart_id='ivan_telegram_id')['data']['id']
    # print(f'{cart_id=}')
    #
    # # customer_cart_association = create_customer_cart_association(
    # #     token,
    # #     cart_id=cart_id,
    # #     customer_id='f8b8e91c-a346-404a-9aef-24838b0ea4da'
    # # )
    # # print(f'{customer_cart_association=}')
    #
    # # print(add_product_to_cart(token, cart_id, f'{first_product_id}'))
    #
    # cart_items = get_cart_items(token, cart_id)
    # print(f'{cart_items=}')
    #
    # # latest_release_of_catalog = get_latest_release_of_catalog(token, catalog_id='7ea1fbee-7653-40b6-8d16-2575db42c508')
    # # print(f'{latest_release_of_catalog=}')


if __name__ == '__main__':
    main()
