"""В этом файле функции которые подгружают необходимые данные из xlsx ДатаСета"""
import pandas as pd
from background_package.distances import get_closest_location


def high_1(input_data: pd.core.frame.DataFrame, available_offices: list[str]) -> dict[str, str]:
    """
    Дата выдачи последней карты более 7 дней назад, при этом есть одобренные заявки ->
    Условие1 для высокого приоритета (Выезд на точку для стимулирования выдач)

    :param input_data: Лист 'Входные данные для анализа' из ДатаСет
    :param available_offices: Массив со всеми офисами
    :return: Словарь, где ключ - адрес точки, значение - ближайший офис
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Кол-во дней после выдачи последней карты",
        "Кол-во одобренных заявок"
    ]

    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] > 7) & (local_data[values_for_look[2]] > 0)
    ]

    for value in filtered_data.values:
        result[str(value[0])] = get_closest_location(str(value[0]), available_offices)

    return result


def high_2(input_data: pd.core.frame.DataFrame, available_offices: list[str]) -> dict[str, str]:
    """
    Дата выдачи последней карты более 14 дней назад ->
    Условие2 для высокого приоритета (Выезд на точку для стимулирования выдач)

    :param input_data: Лист 'Входные данные для анализа' из ДатаСет
    :param available_offices: Массив со всеми офисами
    :return: Словарь, где ключ - адрес точки, значение - ближайший офис
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Кол-во дней после выдачи последней карты"
    ]

    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] > 14)
    ]

    for value in filtered_data.values:
        result[str(value[0])] = get_closest_location(str(value[0]), available_offices)

    return result


def middle_1(input_data: pd.core.frame.DataFrame, available_offices: list[str]) -> dict[str, str]:
    """
    Отношение кол-ва выданных карт к одобренным заявкам менее 50%, если выдано больше 0 карт ->
    Условие1 для среднего приоритета (Обучение агента)

    :param input_data: Лист 'Входные данные для анализа' из ДатаСет
    :param available_offices: Массив со всеми офисами
    :return: Словарь, где ключ - адрес точки, значение - ближайший офис
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Кол-во одобренных заявок",
        "Кол-во выданных карт"
    ]

    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[2]] > 0)
    ]

    for value in filtered_data.values:
        if int(value[2])/int(value[1]) < 1/2:
            result[str(value[0])] = get_closest_location(str(value[0]), available_offices)

    return result


def low_1(input_data: pd.core.frame.DataFrame, available_offices: list[str]) -> dict[str, str]:
    """
    Точка подключена вчера ->
    Условие1 для низкого приоритета (Доставка карт и материалов)

    :param input_data: Лист 'Входные данные для анализа' из ДатаСет
    :param available_offices: Массив со всеми офисами
    :return: Словарь, где ключ - адрес точки, значение - ближайший офис
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Когда подключена точка?"
    ]

    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] == 'вчера')
    ]

    for value in filtered_data.values:
        result[str(value[0])] = get_closest_location(str(value[0]), available_offices)

    return result


def low_2(input_data: pd.core.frame.DataFrame, available_offices: list[str]) -> dict[str, str]:
    """
    Карты и материалы не доставлялись ->
    Условие2 для низкого приоритета (Доставка карт и материалов)

    :param input_data: Лист 'Входные данные для анализа' из ДатаСет
    :param available_offices: Массив со всеми офисами
    :return: Словарь, где ключ - адрес точки, значение - ближайший офис
    """
    result = {}
    values_for_look = [
        "Адрес точки, г. Краснодар",
        "Карты и материалы доставлены?"
    ]

    local_data = input_data.loc[:, values_for_look]
    filtered_data = local_data[
        (local_data[values_for_look[1]] == 'нет')
    ]

    for value in filtered_data.values:
        result[str(value[0])] = get_closest_location(str(value[0]), available_offices)

    return result


def get_workers(path_to_dataset: str, worker_grade='все') -> dict[str, dict[str, str]]:
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
