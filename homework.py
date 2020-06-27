import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PRACTICUM = 'https://praktikum.yandex.ru/api/user_api'


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    statuses = {
        'approved': True,
        'rejected': False
    }
    homework_name = homework.get('homework_name')
    status_homework = statuses.get(homework.get('status'))
    if status_homework is not None:
        if status_homework:
            verdict = (
                f'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
            )
        else:
            verdict = 'К сожалению в работе нашлись ошибки.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'

    return 'Ошибка на сервере: вернулись не верные данные'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    method_url = 'homework_statuses'
    response = {}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            f'{URL_PRACTICUM}/{method_url}/',
            params=params,
            headers=headers
        )
        response = homework_statuses.json()
    except requests.RequestException:
        logging.error('Ошибка подключения к серверу')
        return {}
    except ValueError:
        logging.warning('Ошибка при получении статуса')
        return {}
    return response


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(600)

        except Exception as e:
            logging.critical('bot is down')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
