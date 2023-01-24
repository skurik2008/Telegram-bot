import logging
import requests
import json
from datetime import datetime
import utils
import os
import database


def realization(bot, data=None):
    """
    Функция первого порядка, содержит функции для пошаговой реализации команды /highprice
    :param bot: бот
    :param data: объект класса DataSearch модуля models,
                в который в результате реализации функции вносятся значения-параметры для итогового вывода-результата команды
    :return: функцию get_city (функция следующего шага)
    """
    def get_city(message):
        """
        Функция второго порядка завершает запрос у пользователя названия города и
        запрашивает уточнение названия города или дату заезда.
        Запускает следующую функцию-шаг в зависимости от входящего сообщения пользователя
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            data.city_name = message.text
            response = requests.request("GET", os.getenv('url_id_city'), headers=json.loads(os.getenv('headers')), params={"query": data.city_name})
            res = json.loads(response.text)
            name_city = res.get('suggestions')[0].get('entities')[0].get('name')
            if res.get('moresuggestions') == 0:
                new_message = 'Я не нашел такого города! Попробуйте еще раз!'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_city, repeat_step=True)
                return
            elif name_city != message.text:
                data.city_name = name_city
                new_message = f"Мы ищем этот город - {name_city}?"
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_repeat, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Что-то с названием города у нас не складывается! Попробуйте ввести точнее!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_city, repeat_step=True)
        else:
            new_message = 'Введите дату заезда (число, месяц, год через пробел)\nНапример, 5 6 2022'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_in, repeat_step=False)

    def get_repeat(message):
        """
        Функция второго порядка. Запускается в случае уточняющего вопроса по названию города со стороны бота.
        Запускает повтор либо запрашивает дату заезда и запускает следующую функцию-шаг.
        :param message:блок данных по последнему входящему сообщению пользователя
        """
        if message.text.lower() == 'да':
            new_message = 'Введите дату заезда (число, месяц, год) через пробел\nНапример, 5 6 2022'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_in, repeat_step=False)
        elif message.text.lower() == 'нет':
            new_message = 'Попробуйте вновь ввести название города'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_city, repeat_step=False)
        else:
            new_message = 'Мне нужен ответ: Да/Нет'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_repeat, repeat_step=True)

    def get_check_in(message):
        """
        Функция второго порядка завершает запрос у пользователя даты заезда в отель,
        запрашивает дату выезда и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        current_date = datetime.now()
        try:
            dl = list(map(int, message.text.split(' ')))
            y, m, d = dl[2], dl[1], dl[0]
            check_in = datetime(y, m, d)
            if check_in < current_date:
                new_message = 'Вы возвращаетесь в прошлое?\nВведите дату заезда еще раз'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_in, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Ошибка ввода даты! Попробуйте еще раз!' \
                           '\nНапоминаю правило ввода: число, месяц, год через пробел!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_in, repeat_step=True)
        else:
            data.check_in = check_in
            new_message = 'Введите дату выезда (число, месяц, год) через пробел\nНапример, 5 6 2022'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_off, repeat_step=False)

    def get_check_off(message):
        """
        Функция второго порядка завершает запрос у пользователя даты выезда из отеля,
        запрашивает минимальную цену и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            dl = list(map(int, message.text.split(' ')))
            y, m, d = dl[2], dl[1], dl[0]
            check_off = datetime(y, m, d)
            if check_off < data.check_in:
                new_message = 'Дата выезда должна быть позже даты заезда!\nВведите дату выезда еще раз'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_off, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Неправильный ввод даты! Попробуйте еще раз!' \
                           '\nНапоминаю правило ввода: число, месяц, год через пробел!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_check_off, repeat_step=True)
        else:
            data.check_off = check_off
            new_message = 'Введите минимальную цену ($):'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_price_min, repeat_step=False)

    def get_price_min(message):
        """
        Функция второго порядка завершает запрос у пользователя минимальной цены отеля,
        запрашивает максимальную цену и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if int(message.text) < 0:
                new_message = 'Минимальная цена не должна быть ниже нуля. Повторите ввод!'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_price_min, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Ошибка ввода!\nНапоминаю правила ввода:\nВводится целое (без запятых) число!\nПробуем еще раз!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_price_min, repeat_step=True)
        else:
            data.price_min = message.text
            new_message = 'Введите максимальную цену ($):'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_price_max, repeat_step=False)

    def get_price_max(message):
        """
        Функция второго порядка завершает запрос у пользователя максимальной цены отеля,
        формирует список отелей в диапазоне цен, запрашивает минимальное удаление от центра и
        запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if int(message.text) <= int(data.price_min):
                new_message = 'Максимальная цена должна быть выше указанной вами ранее минимальной цены!\nПовторите ввод!'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_price_max, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Ошибка ввода!\nНапоминаю правила ввода:\nВводится целое (без запятых) число!\nПробуем еще раз!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_price_max, repeat_step=True)
        else:
            new_message = 'Минуточку! Я делаю подбор отелей!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
            data.price_max = message.text
            try:
                hotel_list_in_price_range = utils.creat_hotel_list_in_price_range(data)
                data.hotels_list_range = hotel_list_in_price_range
                if len(hotel_list_in_price_range) > 0:
                    new_message = f'В диапазоне цен: {data.price_min} - {data.price_max} $ найдено отелей: {len(hotel_list_in_price_range)}\n' \
                                  f'Укажите минимальное удаление от центра в милях (от 0.1)'
                    utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_min_distance_center, repeat_step=False)
                else:
                    new_message = f'К сожалению, в диапазоне цен: {data.price_min} - {data.price_max} $ найдено отелей: {len(hotel_list_in_price_range)}\n' \
                                  f'Рекомендую повторить поиск, изменив параметры\n' \
                                  f'(введите команду /bestdeal либо /help)'
                    utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
            except Exception as e:
                new_message = 'Извините, что-то с поиском у меня не сложилось!\nПопробуйте заново!\nВведите /help (список команд)'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)

    def get_min_distance_center(message):
        """
        Функция второго порядка завершает запрос у пользователя минимального удаления отеля от центра,
        запрашивает максимальное удаление от центра и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if float(message.text) < 0.1:
                new_message = 'Минимальное удаление от центра не должно быть меньше 0.1 мили!\nПовторите ввод!'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                                       next_func=get_min_distance_center, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Ошибка ввода!\nНапоминаю правила ввода:\nВводится число больше 0.1 (дробная часть отделяется точкой)\n' \
                          'Пробуем еще раз!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                                   next_func=get_min_distance_center, repeat_step=True)
        else:
            data.distance_min = float(message.text)
            new_message = 'Укажите максимальное удаление от центра в милях.'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                                   next_func=get_max_distance_center, repeat_step=False)

    def get_max_distance_center(message):
        """
        Функция второго порядка завершает запрос у пользователя максимального удаления отеля от центра,
        на базе ранее сформированного списка отелей по диапазону цен формирует список с учетом минимального и максимального удаления от центра,
        запрашивает количество отелей и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if float(message.text) <= float(data.distance_min):
                new_message = f'Максимальное удаление от центра должно быть больше минимального!\n' \
                              f'Введенное вами минимальное удаление: {data.distance_min} mile\n' \
                              f'Повторите ввод максимального удаления от центра.'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                                       next_func=get_max_distance_center, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Ошибка ввода!\nНапоминаю правила ввода:\n' \
                          'Вводится число больше введенного ранее минимального удаления (дробная часть отделяется точкой)\n' \
                          'Пробуем еще раз!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message,
                                   next_func=get_max_distance_center, repeat_step=True)
        else:
            data.distance_max = float(message.text)
            hotels_sort = utils.sort_hotels_by_distance(data.hotels_list_range, data.distance_min, data.distance_max)
            data.hotels_list_range = hotels_sort
            if len(hotels_sort) > 0:
                new_message = f'Диапазон цен: {data.price_min} - {data.price_max} $\n' \
                          f'Удаление от центра: {data.distance_min} - {data.distance_max} миль\n' \
                          f'Найдено отелей: {len(hotels_sort)}\n' \
                          f'Сколько отелей показать (не больше 10)?'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_photo, repeat_step=False)
            else:
                new_message = f'Диапазон цен: {data.price_min} - {data.price_max} $\n' \
                              f'Удаление от центра: {data.distance_min} - {data.distance_max} миль\n' \
                              f'К сожалению, найдено отелей: {len(hotels_sort)}\n' \
                              f'Рекомендую повторить поиск, изменив параметры\n' \
                              f'(введите команду /bestdeal либо /help)'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)

    def get_photo(message):
        """
        Функция второго порядка завершает запрос у пользователя количества отелей для показа,
        запрашивает показ фото отелей и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if int(message.text) > 10 and len(data.hotels_list_range) <= 10 or \
                    int(message.text) <= 10 and int(message.text) > len(data.hotels_list_range) or \
                    int(message.text) > 10 and len(data.hotels_list_range) > 10 or \
                    int(message.text) <= 0:
                if int(message.text) > 10 and len(data.hotels_list_range) <= 10:
                    new_message = f'Во-первых, я просил не больше 10!\n' \
                                  f'Во-вторых, согласно условиям поиска найдено отелей: {len(data.hotels_list_range)}\n' \
                                  f'Попробуем еще раз!\nСколько отелей показать?'
                elif int(message.text) <= 10 and int(message.text) > len(data.hotels_list_range):
                    new_message = f'Согласно условиям поиска найдено отелей: {len(data.hotels_list_range)}\n' \
                                  f'Попробуем еще раз!\nСколько отелей показать?'
                elif int(message.text) > 10 and len(data.hotels_list_range) > 10:
                    new_message = 'Я просил не больше 10. Попробуем еще раз!\nСколько отелей показать?'
                elif int(message.text) <= 0:
                    new_message = 'Меньше ноля и ноль тоже не подходит! Попробуем еще раз!\nСколько отелей показать?'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_photo, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Введите цифру!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_photo, repeat_step=True)
        else:
            data.numbers_hotels = message.text
            new_message = 'Фото отеля показать?'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_number_photo, repeat_step=False)

    def get_number_photo(message):
        """
        Функция второго порядка. Завершает работу команды /bestdeal в случае отказа пользователя от показа фото отелей
        либо запрашивает количество фото для показа и запускает следующую функцию-шаг
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        if message.text.lower() == 'да':
            new_message = 'Сколько фото показать (не больше 5)'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_answer_with_photos, repeat_step=False)
        elif message.text.lower() == 'нет':
            new_message = 'Ожидайте! Я работаю!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
            hotel_list_for_history = list()
            for num, hotel in enumerate(data.hotels_list_range, 1):
                if num <= int(data.numbers_hotels):
                    hotel_list_for_history.append(f"\n{hotel.get('name')} - https://www.hotels.com/ho{hotel.get('id')}")
                    new_message = utils.result_by_hotel_for_bestdeal_command(hotel)
                    utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
                else:
                    break
            hotels_for_history = ', '.join(hotel_list_for_history)
            database.add_value(id_user=message.from_user.id, command='/bestdeal', date=data.time_command,
                               city=data.city_name, value=hotels_for_history)
            new_message = 'Я завершил. Изучайте!\nДля вывода списка команд введите /help'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
        else:
            new_message = 'Я ожидаю ответ: Да/Нет'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_number_photo, repeat_step=True)

    def get_answer_with_photos(message):
        """
        Функция второго порядка. Завершает запрос о количестве фото для показа
        и завершает выполнение команды /bestdeal выводом ее результата
        :param message: блок данных по последнему входящему сообщению пользователя
        """
        try:
            if int(message.text) > 5 or int(message.text) <=0:
                if int(message.text) > 5:
                    new_message = 'Я же просил не больше 5! Попробуем еще раз!\nСколько фото показать?'
                elif int(message.text) <= 0:
                    new_message = 'Меньше ноля и ноль тоже не подходит! Попробуем еще раз!\nСколько фото показать?'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_answer_with_photos, repeat_step=True)
                return
        except Exception as e:
            new_message = 'Введите цифру!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, next_func=get_answer_with_photos, repeat_step=True)
        else:
            new_message = 'Ожидайте! Я работаю!'
            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
            try:
                hotel_list_for_history = list()
                for num, hotel in enumerate(data.hotels_list_range, 1):
                    if num <= int(data.numbers_hotels):
                        hotel_list_for_history.append(f"\n{hotel.get('name')} - https://www.hotels.com/ho{hotel.get('id')}")
                        new_message = utils.result_by_hotel_for_bestdeal_command(hotel)
                        utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
                        querystring = {"id": hotel.get('id')}
                        response = requests.request("GET", os.getenv('url_photos'), headers=json.loads(os.getenv('headers')), params=querystring)
                        response_dict = json.loads(response.text)
                        try:
                            hotel_photo_list = [elem.get('baseUrl') for elem in response_dict.get('hotelImages')]
                            for num in range(int(message.text)):
                                new_message = hotel_photo_list[num].partition('_{size}')[0] + '_z.jpg?impolicy=fcrop&w=500&h=280&q=high'
                                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message, photo_transfer=True)
                        except Exception as e:
                            new_message = 'Извините! Фото этого отеля не нашел!'
                            utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
                            logging.exception(e)
                    else:
                        break
            except Exception as e:
                new_message = 'Извините! Что-то пошло не так! Пожалуйста, повторите поиск!\n' \
                              'Введите /help (список команд)'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
                logging.exception(e)
            else:
                hotels_for_history = ', '.join(hotel_list_for_history)
                database.add_value(id_user=message.from_user.id, command='/bestdeal', date=data.time_command,
                                   city=data.city_name, value=hotels_for_history)
                new_message = 'Я завершил. Изучайте!\nДля вывода списка команд введите /help'
                utils.next_action_func(chat_bot=bot, user_message=message, bot_message=new_message)
    return get_city