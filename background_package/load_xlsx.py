"""В этом файле функции которые подгружают необходимые данные из xlsx ДатаСета"""
import pandas as pd


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

    input_data = pd.read_excel(path_to_dataset, sheet_name='Входные данные для анализа')
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
