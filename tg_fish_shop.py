import os

import redis

from dotenv import load_dotenv
from telegram.ext import Updater, Filters, CallbackQueryHandler, CommandHandler, MessageHandler

from elasticpath_management import (
    add_product_to_cart,
    get_cart_items,
    remove_cart_item,
    create_customer,
    delete_cart
)
from catalog_api import show_menu, show_description_with_image, show_cart

_database = None


def start(update, context):
    show_menu(update, context)
    return 'HANDLE_MENU'


def handle_menu(update, context):
    query = update.callback_query
    query.answer()

    tg_user_id = update.effective_user.id

    if query.data == str(tg_user_id):
        show_cart(update, context, tg_user_id)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return 'HANDLE_CART'

    show_description_with_image(update, context, query.data)
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    query = update.callback_query

    tg_user_id = update.effective_user.id

    if query.data == 'menu':
        show_menu(update, context)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return 'HANDLE_MENU'

    if query.data == str(tg_user_id):
        show_cart(update, context, tg_user_id)
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        return 'HANDLE_CART'

    product_id = query.data.split('_')[0]
    product_quantity = query.data.split('_')[1]

    add_product_to_cart(tg_user_id, product_id, int(product_quantity))
    cart_items = get_cart_items(tg_user_id)

    update.callback_query.answer(text='Товар добавлен в корзину')

    return 'HANDLE_DESCRIPTION'


def handle_cart(update, context):
    query = update.callback_query
    query.answer()

    tg_user_id = update.effective_user.id

    if query.data == 'menu':
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        show_menu(update, context)
        return 'HANDLE_MENU'

    if query.data == 'pay':
        context.bot.send_message(
            chat_id=tg_user_id,
            text='Напишите Ваш email'
        )
        return 'WAITING_EMAIL'

    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
    remove_cart_item(tg_user_id, query.data)
    show_cart(update, context, tg_user_id)

    return 'HANDLE_CART'


def handle_waiting_email(update, context):
    # TODO: Email validator
    tg_user_id = update.effective_user.id
    customer_email = update.message.text
    customer_full_name = f'{update.effective_user.first_name} {update.effective_user.last_name}'

    # TODO: What if customer already exist
    customer = create_customer(customer_full_name, customer_email)

    # TODO: Create something like order
    delete_cart(tg_user_id)

    show_menu(update, context)

    return 'HANDLE_MENU'


def handle_users_reply(update, context):
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
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': handle_waiting_email,
    }

    state_handler = states_functions[user_state]

    next_state = state_handler(update, context)
    db.set(chat_id, next_state)


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


def error_handler(update, context):
    print(context.error)


def main():
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
