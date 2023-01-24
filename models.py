"""Модуль содержит класс данных для поиска"""


class DataSearch:
    """
    Класс оперативного хранения данных в течение выполнения команды
    """

    def __init__(self):
        self.time_command = None
        self.city_name = None
        self.check_in = None
        self.check_off = None
        self.price_min = None
        self.price_max = None
        self.hotels_list_range = None
        self.distance_min = None
        self.distance_max = None
        self.numbers_hotels = None
        self.numbers_photo = None

