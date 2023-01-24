"""Модуль, содержащий вспомогательные функции"""


import requests
import json
import os
import logging


def creat_hotel_list(object, command):
    """
    Функция создает список отелей для команд /lowprice и /highprice
    :param object: объект класса DataSearch модуля models содержит параметры для данного конкретного поиска отелей
    :param command: название выполняемой команды
    :return: список отелей, удовлетворяющих параметрам поиска
    """
    try:
        response = requests.request("GET", os.getenv('url_id_city'), headers=json.loads(os.getenv('headers')), params={"query": object.city_name})
        res = json.loads(response.text)
        city_id = res.get('suggestions')[0].get('entities')[0].get('destinationId')
        if command == 'lowprice':
            sort_index = "PRICE"
        elif command == 'highprice':
            sort_index = "PRICE_HIGHEST_FIRST"
        querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": object.numbers_hotels,
                       "checkIn": object.check_in.strftime('%Y-%m-%d'),
                       "checkOut": object.check_off.strftime('%Y-%m-%d'),
                       "adults1": "1", "sortOrder": sort_index, "locale": "en_US", "currency": "USD"}
        response = requests.request("GET", os.getenv('url_hotels'), headers=json.loads(os.getenv('headers')), params=querystring)
        response_dict = json.loads(response.text)
        hotels_list = response_dict.get('data').get('body').get('searchResults').get('results')
        return hotels_list
    except Exception as e:
        logging.exception(e)

def creat_hotel_list_in_price_range(object):
    """
    Функция создает список отелей для команды /bestdeal в диапазоне цен
    :param object: объект класса DataSearch модуля models содержит параметры для данного конкретного поиска отелей
    :return: список отелей, удовлетворяющих параметрам поиска
    """
    try:
        response = requests.request("GET", os.getenv('url_id_city'), headers=json.loads(os.getenv('headers')),
                                params={"query": object.city_name})
        res = json.loads(response.text)
        id_city = res.get('suggestions')[0].get('entities')[0].get('destinationId')
        querystring = {"destinationId": id_city, "pageNumber": "1", "pageSize": "25",
                       "checkIn": object.check_in.strftime('%Y-%m-%d'),
                       "checkOut": object.check_off.strftime('%Y-%m-%d'), "adults1": "1",
                       "priceMin": object.price_min, "priceMax": object.price_max,
                       "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "en_US", "currency": "USD"}
        intermediate_dict = dict()
        total_list_hotels = list()
        flag = True
        while flag == True:
            response = requests.request("GET", os.getenv('url_hotels'), headers=json.loads(os.getenv('headers')), params=querystring)
            response_dict = json.loads(response.text)
            current_hotels_list = response_dict.get('data').get('body').get('searchResults').get('results')
            if len(current_hotels_list) <= 25:
                for i in current_hotels_list:
                    intermediate_dict.update(
                        {'id': i.get('id'), 'name': i.get('name'), 'streetAddress': i.get('address').get('streetAddress'),
                         'CityCenterDistance': i.get('landmarks')[0].get('distance'),
                         'Price': i.get('ratePlan').get('price').get('current'),
                         'TotalPrice': i.get('ratePlan').get('price').get('fullyBundledPricePerStay')})
                    inter_dict = intermediate_dict.copy()
                    total_list_hotels.append(inter_dict)
                if len(current_hotels_list) < 25:
                    flag = False
                else:
                    querystring['pageNumber'] = str(int(querystring.get('pageNumber')) + 1)
        return total_list_hotels
    except Exception as e:
        logging.exception(e)
        return None

def sort_hotels_by_distance(list_hotels, min, max):
    """
    Функция создает список отелей для команды /bestdeal в указанном диапазоне удаления от центра города
    :param list_hotels: список отелей
    :param min: минимальное расстояние от центра города
    :param max: максимальное расстояние от центра города
    :return: список отелей в диапазоне удаления от центра города
    """
    answer_list_hotels = list()
    for hotel in list_hotels:
        distance = float(hotel.get('CityCenterDistance').partition(' ')[0])
        if distance > min and distance < max:
            answer_list_hotels.append(hotel)
    return answer_list_hotels


def result_by_hotel(hotel_d):
    """
    Функция создает текст сообщения-ответа в чат бота по каждому отелю
    :param hotel_d: словарь с данными конкретного отеля из сформированного в результате выполнения команды списка
    :return: текстовое сообщение-ответ
    """
    result = f"Name hotel: {hotel_d['name']}" \
             f"\nAdress: {hotel_d.get('address').get('streetAddress', 'Non street')}" \
             f"\nProximity to the center: {hotel_d.get('landmarks')[0].get('distance')}" \
             f"\nPrice: {hotel_d.get('ratePlan').get('price').get('current')}" \
             f"\nTotal price: {hotel_d.get('ratePlan').get('price').get('fullyBundledPricePerStay', 'no data').replace('&nbsp;', ' ')}" \
             f"\nPage on the site: https://www.hotels.com/ho{hotel_d.get('id')}\n"
    return result

def result_by_hotel_for_bestdeal_command(hotel_dt):
    """
    Функция создает текст сообщения-ответа в чат бота по каждому отелю для команды /bestdeal
    :param hotel_dt: словарь с данными конкретного отеля из сформированного в результате выполнения команды списка
    :return: текстовое сообщение-ответ
    """
    result = f"Name hotel: {hotel_dt['name']}" \
             f"\nAdress: {hotel_dt.get('streetAddress')}" \
             f"\nProximity to the center: {hotel_dt.get('CityCenterDistance')}" \
             f"\nPrice: {hotel_dt.get('Price')}" \
             f"\nTotal price: {hotel_dt.get('TotalPrice').replace('&nbsp;', ' ')}" \
             f"\nPage on the site: https://www.hotels.com/ho{hotel_dt.get('id')}"
    return result

def next_action_func(chat_bot, user_message, bot_message, photo_transfer=None, next_func=None, repeat_step=None):
    """
    Функция, запускающая следующее действие-шаг в боте
    :param chat_bot: бот
    :param user_message: входящее сообщение пользователя
    :param bot_message: ответное сообщение бота
    :param photo_transfer: True - запускает функцию вывода в чат фото
    :param next_func: функция, которую нужно запустить следующим шагом
    :param repeat_step: True - запускает повторно текущую функцию, False - запускает следующую функцию-шаг
    """
    try:
        if repeat_step == True:
            msg = chat_bot.send_message(user_message.chat.id, bot_message)
            chat_bot.register_next_step_handler(msg, next_func)
        elif repeat_step == False:
            chat_bot.send_message(user_message.chat.id, bot_message)
            chat_bot.register_next_step_handler(user_message, next_func)
        elif photo_transfer == True:
            chat_bot.send_photo(user_message.chat.id, bot_message)
        else:
            chat_bot.send_message(user_message.chat.id, bot_message)
    except Exception as e:
        logging.exception(e)

