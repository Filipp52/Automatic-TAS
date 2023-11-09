"""В этом файле функции для работы с расстояниями и вычислениями оптимальных точек"""
from functools import lru_cache
import requests
from geopy.distance import geodesic


@lru_cache()  # Кэширования входных данных и результата функции для ускорения процесса
def get_geocode(address: str) -> tuple:
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

    try:
        # Отправка GET-запроса и получение ответа в формате JSON
        response = requests.get(url)

        # Проверка статуса ответа
        if response.status_code == 200:
            incorrect_geo = dict(response.json())['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
            return incorrect_geo[1], incorrect_geo[0]
        else:
            print("Ошибка при выполнении запроса. Статус код:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Ошибка при выполнении запроса:", e)


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
