"""В этом файле функции для работы с расстояниями и вычислениями оптимальных точек"""
import pickle
from functools import lru_cache
import requests
from geopy.distance import geodesic
from settings import path2pgc


@lru_cache()  # Кэширования входных данных и результата функции для ускорения процесса
def ask_geocode_yandex(address: str) -> tuple:
    """
    Преобразует ваш адрес в координаты

    :param address: Адрес локации
    :return: (длина, широта)
    """
    # TODO: избежать такого
    ##########################################################################
    if not address.count('Краснодар'):
        address = f"Краснодар, {address}"
    if address.count('ул. им. Героя Аверкиева А.А.'):
        address.replace('ул. им. Героя Аверкиева А.А.', 'ул. Героя Аверкиева')
    ##########################################################################

    yandex_api_key = 'd41bf1b3-cd46-4b67-a626-3725ead0cd11'
    url = f'https://geocode-maps.yandex.ru/1.x/?apikey={yandex_api_key}&geocode={address}&format=json'

    response = requests.get(url)

    if response.status_code == 200:
        incorrect_geo = dict(response.json())['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        return incorrect_geo[1], incorrect_geo[0]
    else:
        raise Exception('Что-то не так с Yandex API')


@lru_cache()  # Кэширования входных данных и результата функции для ускорения процесса
def get_geocode(address: str) -> tuple:
    """
    Парсит PickleGeoCode в надежде найти там уже преобразованный адрес
    Если же нет, то отправляется запрос в яндекс и записывается в pgc на будущее

    :param address: Адрес локации
    :return: (длина, ширина)
    """
    with open(path2pgc, 'rb') as picle_geocodes:
        geocodes = dict(pickle.load(picle_geocodes))
    if address in geocodes:
        return geocodes[address]
    geo = ask_geocode_yandex(address)
    geocodes[address] = geo
    with open(path2pgc, 'wb') as picle_geocodes:
        pickle.dump(geocodes, picle_geocodes)
    return geo


def get_closest_location(static_point: str, locations: list[str]) -> str:
    """
    Находит ближайшую точку (по расстоянию) из массива 'locations' к точке 'static_point'

    :param static_point: Исходная локация, к которой мы ищем ближайшую точку
    :param locations: Массив локаций, из которого мы выберем ближайшую точку
    :return: Ближайшая точка из массива
    """
    geocode_of_static_point = get_geocode(static_point)
    closest_location = ""
    closest_distance = float('inf')

    for location in locations:
        geocode = get_geocode(location)
        distance = geodesic(geocode_of_static_point, geocode).kilometers

        if distance < closest_distance:
            closest_location = location
            closest_distance = distance

    return closest_location
