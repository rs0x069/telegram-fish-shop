# Телеграм-бот по продаже рыбы

*Проект сделан в учебных целях в рамках курсов web-разработчиков [dvmn](https://dvmn.org).*

Телеграм-бот по продаже рыбы. Можно посмотреть товар, положить в корзину, оформить покупку.\
Работает по API с системой электронной коммерции [elasticpath](https://www.elasticpath.com/).\
Для хранения этапов покупки используется онлайн-сервис БД Redis [redislabs](https://redislabs.com/).\
Бот работает на сервисе [Heroku](https://heroku.com/).

## Требования
Python 3.8, 3.9 или 3.10.

### Зависимые модули
* requests==2.28.1
* python-telegram-bot==13.13
* python-dotenv==0.20.0
* redis==4.3.4

## Предварительные требования
1. Для телеграм бота необходимо создать бота в Телеграм и получить токен. Разрешить боту отправлять вам уведомления.
2. На сервисе [elasticpath](https://www.elasticpath.com/) создать каталог товаров.

## Установка
* Склонировать проект
```commandline
git clone https://github.com/rs0x069/telegram-fish-shop.git && cd telegram-fish-shop
```
* Установить зависимые пакеты
```commandline
pip install -r requirements.txt
```
* Создать файл `.env` со следующими переменными окружения:
  + `TELEGRAM_TOKEN` - токен телеграм бота.
  + `ELASTICPATH_STORE_ID`
  + `ELASTICPATH_CLIENT_ID`
  + `ELASTICPATH_CLIENT_SECRET`
  + `REDIS_HOST` - адрес базы данных Redis
  + `REDIS_PORT` - порт базы данных Redis
  + `REDIS_USERNAME` - имя пользователя для доступа к базе данных Redis
  + `REDIS_PASSWORD` - пароль для доступа к базе данных Redis

## Использование
* Для запуска телеграм бота запустить скрипт `tg_fish_shop.py`
```commandline
python tg_fish_shop.py
```

## Пример
![Пример результата для Telegram](https://raw.githubusercontent.com/rs0x069/telegram-fish-shop/main/.github/images/fish-shop.gif)

***
Учебный проект для курсов web-разработчиков [dvmn](https://dvmn.org). 