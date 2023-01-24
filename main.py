"""Основной скрипт, запускающий Telegram_bot и обеспечивающий его работу"""


import telebot
import os
import commands
import lowprice, highprice, bestdeal, history
from dotenv import load_dotenv
import logging
import database


if __name__ == '__main__':
    file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(file_path):
        load_dotenv(file_path)

    logging.basicConfig(filename='errors.log',
                        format='\n%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                        datefmt='%d.%m.%Y г. %H:%M:%S',
                        level=logging.ERROR)

    database.init_table()

    bot = telebot.TeleBot(os.getenv('token'))
    commands.command_history(bot)
    commands.command_bestdeal(bot)
    commands.command_highprice(bot)
    commands.command_lowprice(bot)
    commands.start_and_help(bot)
    lowprice.realization(bot)
    highprice.realization(bot)
    bestdeal.realization(bot)
    history.realization(bot)
    commands.text(bot)

    bot.infinity_polling()