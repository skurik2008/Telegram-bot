import time
import lowprice, highprice, bestdeal, history
import utils
from models import DataSearch


def start_and_help(bot):
    @bot.message_handler(commands=['help', 'start'])
    def func_for_commands(message):
        help = "/lowprice - самые дешевые отели в городе\n" \
               "/highprice - самые дорогие отели в городе\n" \
               "/bestdeal - отели, подходящие по цене и расположению к центру\n" \
               "/history - история поиска отеля\n" \
               "/help - список команд"
        if message.text == '/start':
            new_message = f'Приветствую!\nВот список моих команд:\n{help}'
        elif message.text == '/help':
            new_message = f'Вот список моих команд:\n{help}'
        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)

def command_lowprice(bot):
    """
    Функция-обработчик команды /lowprice
    :param bot: бот
    """
    @bot.message_handler(commands=['lowprice'])
    def func(message):
        """
        Функция-ответ на команду /lowprice, запрашивающая название города и запускающая функцию пошаговой реализации команды
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        data1 = DataSearch()
        time_command = time.strftime('%d.%m.%Y г. %H:%M')
        data1.time_command = time_command
        new_message = 'Где будем искать? Введите название города!'
        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                               next_func=lowprice.realization(bot=bot, data=data1), repeat_step=False)

def command_highprice(bot):
    """
    Функция-обработчик команды /highprice
    :param bot: бот
    """
    @bot.message_handler(commands=['highprice'])
    def func(message):
        """
        Функция-ответ на команду /highrice, запрашивающая название города и запускающая функцию пошаговой реализации команды
        :param message:
        :return: блок данных по последнему входящему сообщению пользователя
        """
        data1 = DataSearch()
        time_command = time.strftime('%d.%m.%Y г. %H:%M')
        data1.time_command = time_command
        new_message = 'Где будем искать? Введите название города!'
        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                               next_func=highprice.realization(bot=bot, data=data1), repeat_step=False)

def command_bestdeal(bot):
    """
    Функция-обработчик команды /bestdeal
    :param bot: бот
    """
    @bot.message_handler(commands=['bestdeal'])
    def func(message):
        """
        Функция-ответ на команду /highrice, запрашивающая название города и запускающая функцию пошаговой реализации команды
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        data1 = DataSearch()
        time_command = time.strftime('%d.%m.%Y г. %H:%M')
        data1.time_command = time_command
        new_message = 'Где будем искать? Введите название города!'
        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                               next_func=bestdeal.realization(bot=bot, data=data1), repeat_step=False)

def command_history(bot):
    """
    Функция-обработчик команды /history
    :param bot: бот
    """
    @bot.message_handler(commands=['history'])
    def func(message):
        """
        Функция-ответ на команду /history, запрашивающая дату для вывода истории
        и запускающая функцию реализации команды
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        date_now = time.strftime('%d.%m.%Y г.')
        new_message = f'Сегодня {date_now}.\n' \
                      f'Просмотр истории возможен за период 7 дней!\n' \
                      f'Правила ввода:\n' \
                      f'История за сегодня - введите 0\n' \
                      f'История за вчера (или один день назад) - введите 1\n' \
                      f'История за позавчера (или два дня назад) - введите 2 и т.д.\n' \
                      f'Максимально 7 дней назад!'
        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                               next_func=history.realization(bot=bot), repeat_step=False)

def text(bot):
    """
    Функция-обработчик текстового сообщения пользователя,
    поступающего от пользователя не в рамках реализации какой-либо из команд
    :param bot: бот
    """
    @bot.message_handler(content_types=["text"])
    def repeat(message):
        new_message = 'Извините! Я не понял!'
        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)