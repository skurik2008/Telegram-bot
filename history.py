import database
from datetime import datetime, timedelta
import utils

def realization(bot):
    """
    Функция первого порядка, содержит функцию для реализации команды /history
    :param bot: бот
    :return: функцию get_history (функция второго порядка)
    """
    def get_history(message):
        """
        Функция второго порядка. Завершает запрос у пользователя даты для вывода истории и выводит ответ
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if int(message.text) < 0 or int(message.text) > 7:
                new_message = 'Неверный ввод!\n' \
                              'Введите цифру от 0 до 7 включительно!\n' \
                              '(0 - история за сегодня, 1 - вчера, 2 - позавчера ...... 7 - неделю назад)'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_history, repeat_step=True)
            else:
                date_history = (datetime.now() - timedelta(int(message.text))).strftime('%d.%m.%Y')
                history_data = database.select_data(user=message, date=date_history)
                if history_data:
                    for str_in_table in history_data:
                        new_message = f'Команда: {str_in_table[0]}\n' \
                                      f'Дата и время ввода: {str_in_table[1]}\n' \
                                      f'Город: {str_in_table[2]}\n' \
                                      f'Результат поиска:' \
                                      f'{str_in_table[3]}\n'
                        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
                    new_message = 'Введите /help (список команд)'
                    utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
                else:
                    new_message = f'Извините! За {date_history} данных нет!\n' \
                                  f'Попробуйте изменить дату поиска!\n' \
                                  f'Повторить: /history. Список команд: /help'
                    utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
        except Exception as e:
            new_message = 'Ошибка ввода!\n' \
                          'Введите цифру от 0 до 7 включительно!\n' \
                          '(0 - история за сегодня, 1 - вчера, 2 - позавчера ...... 7 - неделю назад)'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_history,
                                   repeat_step=True)
    return get_history


