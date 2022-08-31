import os

import redis

from functools import partial

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Filters, CallbackQueryHandler, CommandHandler, MessageHandler

from elasticpath_management import *

_database = None


# def start(bot, update, elasticpath_token):
def start(update, context, elasticpath_token):
    """
    Хэндлер для состояния START.

    Бот отвечает пользователю фразой "Привет!" и переводит его в состояние ECHO.
    Теперь в ответ на его команды будет запускаеться хэндлер echo.
    """

    keyboard_buttons = []

    products = get_all_products(elasticpath_token)
    for product in products['data']:
        keyboard_buttons.append(
            [
                InlineKeyboardButton(text=product['attributes']['name'], callback_data=product['id'])
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard_buttons)

    update.message.reply_text(text='Please choose:', reply_markup=reply_markup)

    return 'HANDLE_MENU'


def handle_menu(update, context, elasticpath_token):
    query = update.callback_query

    query.answer()

    product = get_product(elasticpath_token, query.data)
    product_description = product['data']['attributes']['description']

    query.edit_message_text(text=product_description)

    return 'START'


def handle_users_reply(update, context, elasticpath_token):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(update, context, elasticpath_token)
        db.set(chat_id, next_state)
    except Exception as err:
        print(f'Exception: {err}')


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
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

    handle_users_reply_ep_token = partial(handle_users_reply, elasticpath_token=elasticpath_token)

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply_ep_token))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply_ep_token))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply_ep_token))

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
