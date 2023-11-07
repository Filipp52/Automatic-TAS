"""
Краткая выжимка:
Этот файл - песочница для MatveyFilippov
Этот код требует большой доработки, прямо сейчас это просто наброски моего мнения о пути для Бэка

Интересные строчки (чтоб не читать весь код):
1) строка 45 - функция демонстрирует как можно работать с excel файлами
2) строка 248 - функция демонстрирует проблему с геопозициями
3) строка 297 - обобщение и пример использования функций
"""
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from functools import lru_cache
import threading  # ненужный импорт, можно удалить
import time  # ненужный импорт, можно удалить
import json
# TODO: pip install openpyxl


##########################################################################################################
# import certifi
# import geopy.geocoders
# import ssl

# geopy.geocoders.options.default_ssl_context = ssl.create_default_context(cafile=certifi.where())

# Не имею представления зачем нужна эта строчка, но определение геолокации без неё не работает
# При этом, когда я до этого в своих проектах использовал geopy никаких проблем не было

# Попробуйте запустить без неё, если же всё-таки при определении позиции вы получите ошибку:
# geopy.exc.GeocoderServiceError: [SSL: CERTIFICATE_VERIFY_FAILED]: unable to get local issuer certificate
# То нужно вернуть в код эту строчку
##########################################################################################################
geolocator = Nominatim(user_agent="my_app")
path2dataset = "ДатаСет_Финал.xlsx"
###############################################################################################
# input_data = pd.read_excel(path2dataset, sheet_name='Входные данные для анализа')

# Сейчас код реализован так, что в функции мы передаём путь к таблице и каждый раз открываем её
# Можно открыть таблицу 1 раз в начале и передавать в функцию её (вместо пути)
# Я не знаю как лучше, если что, поменять это - изи
###############################################################################################


def high_1(path_to_dataset: str) -> dict[str, dict[str, int]]:
    """
    Дата выдачи последней карты более 7 дней назад, при этом есть одобренные заявки ->
    Условие1 для высокого приоритета (Выезд на точку для стимулирования выдач)

    :param path_to_dataset: путь где лежит исходный excel файл
    :return: словарь, где ключ - адрес точки, значение - словарь (ключ - параметр, значение - число)
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Кол-во дней после выдачи последней карты",
        "Кол-во одобренных заявок"
    ]

    input_data = pd.read_excel(path_to_dataset, sheet_name='Входные данные для анализа')  # это действие можно убрать - см строчку №37
    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] > 7) & (local_data[values_for_look[2]] > 0)
    ]

    for value in filtered_data.values:
        result[str(value[0])] = {
            values_for_look[1]: int(value[1]),
            values_for_look[2]: int(value[2])
        }

    return result


def high_2(path_to_dataset: str) -> dict[str, int]:
    """
    Дата выдачи последней карты более 14 дней назад ->
    Условие2 для высокого приоритета (Выезд на точку для стимулирования выдач)

    :param path_to_dataset: путь где лежит исходный excel файл
    :return: словарь, где ключ - адрес точки, значение - кол-во дней после последней выдачи карты
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Кол-во дней после выдачи последней карты"
    ]

    input_data = pd.read_excel(path_to_dataset, sheet_name='Входные данные для анализа')  # это действие можно убрать - см строчку №37
    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] > 14)
    ]

    for value in filtered_data.values:
        result[str(value[0])] = int(value[1])

    return result


def middle_1(path_to_dataset: str) -> dict[str, dict[str, float | int]]:
    """
    Отношение кол-ва выданных карт к одобренным заявкам менее 50%, если выдано больше 0 карт ->
    Условие1 для среднего приоритета (Обучение агента)

    :param path_to_dataset: путь где лежит исходный excel файл
    :return: словарь, где ключ - адрес точки, значение - - словарь (ключ - параметр, значение - число)
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Кол-во одобренных заявок",
        "Кол-во выданных карт"
    ]

    input_data = pd.read_excel(path_to_dataset, sheet_name='Входные данные для анализа')  # это действие можно убрать - см строчку №37
    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[2]] > 0)
    ]

    for value in filtered_data.values:
        ratio = int(value[2])/int(value[1])
        if ratio < 1/2:
            result[str(value[0])] = {
                values_for_look[2]: int(value[2]),
                values_for_look[1]: int(value[1]),
                'Соотношение': ratio
            }

    return result


def low_1(path_to_dataset: str) -> list[str]:
    """
    Точка подключена вчера ->
    Условие1 для низкого приоритета (Доставка карт и материалов)

    :param path_to_dataset: путь где лежит исходный excel файл
    :return: массив, где значение - адрес точки
    """
    result = []
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Когда подключена точка?"
    ]

    input_data = pd.read_excel(path_to_dataset, sheet_name='Входные данные для анализа')  # это действие можно убрать - см строчку №37
    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] == 'вчера')
    ]

    for value in filtered_data.values:
        result.append(str(value[0]))

    return result


def low_2(path_to_dataset: str) -> list[str]:
    """
    Карты и материалы не доставлялись ->
    Условие2 для низкого приоритета (Доставка карт и материалов)

    :param path_to_dataset: путь где лежит исходный excel файл
    :return: массив, где значение - адрес точки
    """
    result = []
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Карты и материалы доставлены?"
    ]

    input_data = pd.read_excel(path_to_dataset, sheet_name='Входные данные для анализа')  # это действие можно убрать - см строчку №37
    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] == 'нет')
    ]

    for value in filtered_data.values:
        result.append(str(value[0]))

    return result


def get_workers(path_to_dataset: str, worker_grade: str | None = 'все') -> dict[str, dict[str, str]]:
    """
    Преобразуем xlsx в dict (для раздела с работниками)

    :param path_to_dataset: путь где лежит исходный excel файл
    :param worker_grade: Если вписать, то будет словарь только с работниками определённого уровня
    Если оставить пустым, то вернёт всех работников
    :return: словарь, где ключ - ФИО, значение - словарь с параметрами работника
    """
    result = {}

    input_data = pd.read_excel(path_to_dataset, sheet_name='Справочник сотрудников')
    if worker_grade != 'все':
        input_data = input_data[
            (input_data['Грейд'] == worker_grade)
        ]

    for value in input_data.values:
        result[str(value[0])] = {
            "Адрес": str(value[1]),
            "Грейд": str(value[2])
        }

    return result


# TODO: нужно сделать функцию, которая бы во время добавления нового адреса записывала бы в бд её координаты или другие параметры для сравнения расстояний
@lru_cache()  # Кеширование результата выполнения функции для ускорения процесса вычисления
def location_to_geocode(location: str) -> tuple:
    """
    Преобразует адрес в координаты

    :param location: Адрес
    :return: Широта, долгота
    """
    location_point = geolocator.geocode(location)
    return location_point.latitude, location_point.longitude


def find_closest_location(point_to_go: str, worker_locations: list) -> str:
    """
    Находит ближайшую локацию, беря координаты мест и сравнивая расстояние в километрах

    :param point_to_go: Адрес куда нужно будет выехать специалисту
    :param worker_locations: Массив с адресами всех локаций работников
    :return: Ближайший офис к точке, на которую нужно выехать
    """
    geocode_of_point_to_go = location_to_geocode(point_to_go)
    closest_location = ""
    closest_distance = float('inf')

    for location in worker_locations:
        geocode = location_to_geocode(location)
        distance = geodesic(geocode_of_point_to_go, geocode).kilometers

        if distance < closest_distance:
            closest_location = location
            closest_distance = distance

    return closest_location


def bad_example_of_location():
    """
    Пример функции, показывающий невозможность использования данного алгоритма для вычисления координатов

    На мой взгляд есть 2 решения:
    1) Использовать другой метод, например, API к Яндекс.Карты
    2) Хранить адреса в удобном для нас виде (в блоке except написано в чём ошибка -> её можно избежать)
    """
    data = pd.read_excel(path2dataset, sheet_name='Входные данные для анализа').loc[:, ["Адрес точки, г. Краснодар"]]
    num_of_ex = 0

    for value in data.values:
        print(f"Краснодар, {str(value[0])} ", end="")
        try:
            geo = location_to_geocode("Краснодар, " + str(value[0]))
            print(geo)
        except Exception:
            # В основном, как я понял, он кидает ошибку по причине некорректной записи адреса
            # Например, 'Краснодар, ул. им. Дзержинского, д. 100' - ошибка
            # Но если убрать из строчки 'им.' - всё ок и программа выдаёт координаты
            print(None)
            num_of_ex += 1

    print(f"\nЧисло ошибок = {num_of_ex}; Это {num_of_ex / len(data.values)} %")


def loading_animation():  # TODO: удалить эту функцию
    """
    Совершенно ненужная функция, она не несёт в себе никакого смысла, это просто для красоты
    """
    for i, symbol in enumerate("Loading"):
        if i == 4 or i == 0:
            for _ in range(3 if i == 0 else 1):
                print("|", end="")
                time.sleep(0.5)
                print("\b", end="")
                time.sleep(0.5)
        print(symbol, end="")
        time.sleep(0.25)
    for i in range(4):
        print(".", end=" ")
        time.sleep(0.5)
    print("\b"*8, end="")
    time.sleep(0.5)
    print(".", end=" ")
    time.sleep(0.5)
    print("\b"*9, end="")


# Далее будет приведён пример использования всех этих функций
#############################################################

# Получение всех адресов для тасков (и их метрик)
thread = threading.Thread(target=loading_animation)
thread.start()

locations_for_first_task = {
    'Условие1': high_1(path2dataset),
    'Условие2': high_2(path2dataset)
}
locations_for_second_task = middle_1(path2dataset)
locations_for_third_task = {
    'Условие1': low_1(path2dataset),
    'Условие2': low_2(path2dataset)
}

# Для 1 таска нам подойдут только специалисты синьоры
seniors = get_workers(path2dataset, "Синьор")
all_available_seniors_loc = []

for values in seniors.values():
    if values['Адрес'] not in all_available_seniors_loc:
        all_available_seniors_loc.append(values['Адрес'])

# Берём задачу и назначаем специалиста
if locations_for_first_task['Условие1'] != {}:
    for point in locations_for_first_task['Условие1']:
        try:
            closest_senior_loc = find_closest_location(point, all_available_seniors_loc)  # Плохо работает. Почему? Смотри в bad_example_of_location()
        except Exception:
            continue
        for name_of_senior, value in seniors.items():
            if value['Адрес'] == closest_senior_loc:
                thread.join()
                print(f"На задание 'Выезд на точку для стимулирования выдач' по адресу {point} нужно отправить {name_of_senior}")
                # Тут описан не полный способ и не все мелочи учтены - это просто пример для визуализации моих мыслей
                # TODO: накинуть всяких проверок для работника, подбирать задачи только поблизости, учитывать время выполнения и тд
                break
        break
elif locations_for_first_task['Условие2'] != {}:
    pass  # Сделать что-то по типу того, что написано выше
else:
    pass  # Сделать что-то подобное для всех типов задач


# Явные минусы и их возможные решения:
# 1) Не очень быстрые вычисления + если сервер нечаянно остановится во время подготовки - потеряем всё разом
# Решение:
# Можно переписать код на рекурсию и каждый полученный адрес записывать сразу (не дожидаясь всех вычислений в ТПО)
#
# 2) Вышеуказанная проблема с геолокациями
# Решение:
# Использовать удобные для нас адреса или другой метод API (например Яндекс.Карты)
#
# 3) Отсутствие try-except, проверок о прочих мелочей для стабильной работы
# Решение:
# Дописать ;)
#


# Далее будет приведён пример JsonMemoryCommunication
#####################################################

jmc = {
    "ФИО/ID работника": {
        "Кол-во заданий": "число заданий на день (кол-во элементов массивов в разделе задания)",
        "Исходная локация": "изначальное местоположение работника",
        "Задания (ключи словаря расставлены в нужной последовательности)": {
            "Адрес1": ["Название задания 1", "Название задания 2"],
            "Адрес2": ["Название задания 3"],
            "Адрес3": ["Название задания 4"]
        }
    },
    "Дерягин Никита Владимирович": {
        "Кол-во заданий": 3,
        "Исходная локация": "Краснодар, Красная, д. 139",
        "Задания": {
            "тер. Пашковский жилой массив, ул. Крылатая, д. 2": ["Выезд на точку для стимулирования выдач"],
            "ул. им. Селезнева, д. 197/5": ["Обучение агента"],
            "ул. им. Героя Аверкиева А.А., д. 8": ["Обучение агента"]
        }
    },
    "Иванов Адам Федорович": {
        "Кол-во заданий": 2,
        "Исходная локация": "Краснодар, В.Н. Мачуги, 41",
        "Задания": {
            "ул. Северная, д. 389": ["Выезд на точку для стимулирования выдач"],
            "ул. Красных Партизан, д. 439": ["Выезд на точку для стимулирования выдач"]
        }
    },
    "Андреев Гордий Данилович": {
        "Кол-во заданий": 3,
        "Исходная локация": "Краснодар, В.Н. Мачуги, 41",
        "Задания": {
            "ул. Красная, д. 149": ["Выезд на точку для стимулирования выдач", "Обучение агента"],
            "ул. Красная, д. 176": ["Доставка карт и материалов"]
        }
    }
}

with open("jmc_example.json", "w") as jmc_file:
    json.dump(jmc, jmc_file, ensure_ascii=False)
