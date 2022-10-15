import textwrap

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import PARSEMODE_MARKDOWN_V2
from telegram_bot_pagination import InlineKeyboardPaginator

from elasticpath_management import (
    get_product,
    get_all_products,
    get_product_files,
    get_file_by_id,
    get_cart_items
)


def show_menu(update, context):
    tg_user_id = update.effective_chat.id

    products = get_all_products()
    keyboard_buttons = []
    for product in products['data']:
        keyboard_buttons.append(
            [
                InlineKeyboardButton(text=product['attributes']['name'], callback_data=product['id'])
            ]
        )
    keyboard_buttons.append([InlineKeyboardButton(text='Корзина', callback_data=str(tg_user_id))])

    reply_markup = InlineKeyboardMarkup(keyboard_buttons)

    # paginator = InlineKeyboardPaginator(page_count=2)
    # # paginator.add_before(button for button in keyboard_buttons)
    # paginator.add_before(
    #     InlineKeyboardButton('Like', callback_data='like#{}'.format(1)),
    #     InlineKeyboardButton('Dislike', callback_data='dislike#{}'.format(2)),
    #     InlineKeyboardButton('Dislike', callback_data='dislike#{}'.format(3)),
    # )
    # paginator.add_after(InlineKeyboardButton(text='Корзина', callback_data=str(tg_user_id)))

    menu = context.bot.send_message(
        chat_id=tg_user_id,
        text='*Выберите товар:*',
        reply_markup=reply_markup,
        # reply_markup=paginator.markup,
        parse_mode=PARSEMODE_MARKDOWN_V2
    )

    return menu


def show_description_with_image(update, context, query_data):
    tg_user_id = update.effective_chat.id

    product = get_product(query_data)
    product_id = product['data']['id']
    product_description = product['data']['attributes']['description']

    product_files = get_product_files(product_id)

    product_files_ids = product_files['data'][0]['id']

    file = get_file_by_id(product_files_ids)
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


def show_cart(update, context, tg_user_id):
    cart_items = get_cart_items(tg_user_id)

    cart = '*Корзина:*\n\n'
    for cart_item in cart_items['data']:
        product_quantity = cart_item['quantity']
        product_per_cost = cart_item['unit_price']['amount']
        product_amount = cart_item['value']['amount']

        cart += textwrap.dedent(f"""\
                *{cart_item['name']}*
                _{cart_item['description']}_
                ${product_per_cost} per kg
                {product_quantity}kg in cart for ${product_amount}

                """)

    cart_amount = cart_items['meta']['display_price']['with_tax']['amount']
    cart += f'*Total: ${cart_amount}*'

    keyboard = []
    for cart_item in cart_items['data']:
        keyboard.append(
            [
                InlineKeyboardButton(text=f"Удалить из корзины: {cart_item['name']}", callback_data=cart_item['id'])
            ]
        )
    keyboard.append([InlineKeyboardButton('Оплатить', callback_data='pay')])
    keyboard.append([InlineKeyboardButton('Меню', callback_data='menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    cart = context.bot.send_message(
        chat_id=tg_user_id,
        text=cart,
        reply_markup=reply_markup,
        parse_mode=PARSEMODE_MARKDOWN_V2
    )

    return cart
