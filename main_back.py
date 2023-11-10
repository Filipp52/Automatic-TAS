"""В этом файле сборка которая запускается в 00:00 и высчитывать работников и их задачи"""
from background_package.load_xlsx import high_1, high_2, low_1, low_2, get_workers, middle_1
import pandas as pd
from background_package.work_with_jmc import get_jmc, write_worker_in_jmc
from settings import path2dataset, path2jmc, path2ntt, today_date, yesterday_date


hours_per_task = {
    "Выезд на точку для стимулирования выдач": 4,
    "Обучение агента": 2,
    "Доставка карт и материалов": 1.5
}


workers = get_workers(path_to_dataset=path2dataset)

# Получаем список, с офисами каждого грейда
seniors_offices = []
seniors_a_midl_offices = []
all_offices = []

for value in workers.values():
    if value['Грейд'] == 'Синьор':
        seniors_offices.append(value['Адрес'])
        seniors_a_midl_offices.append(value['Адрес'])
        all_offices.append(value['Адрес'])
    elif value['Грейд'] == 'Мидл':
        seniors_a_midl_offices.append(value['Адрес'])
        all_offices.append(value['Адрес'])
    else:
        all_offices.append(value['Адрес'])
seniors_offices = list(set(seniors_offices))
seniors_a_midl_offices = list(set(seniors_a_midl_offices))
all_offices = list(set(all_offices))


# Получаем задачи и офисы рядом с ними
data_about_locations = pd.read_excel(path2dataset, sheet_name='Входные данные для анализа')
locations_for_first_task = {
    'Условие1': high_1(data_about_locations, seniors_offices),
    'Условие2': high_2(data_about_locations, seniors_offices)
}
locations_for_second_task = middle_1(data_about_locations, seniors_a_midl_offices)
locations_for_third_task = {
    'Условие1': low_1(data_about_locations, all_offices),
    'Условие2': low_2(data_about_locations, all_offices)
}

temp_result = {}  # Сюда мы записываем работника и массив с его заданиями

# Смотрим есть ли невыполненные задачи
try:
    old_tasks = get_jmc(path2jmc, yesterday_date)
except KeyError:  # Если вчера не было ничего
    old_tasks = {}
for worker_id in old_tasks:
    for old_street, old_task in old_tasks[worker_id]['Задания'].items():
        if list(old_task.values())[0] == 'Не выполнено':
            created_old_task = {'Задание': list(old_task.keys())[0], 'Адрес': old_street}
            if worker_id not in temp_result:
                temp_result[worker_id] = {
                    'Задания': [created_old_task],
                    'Свободных часов': 8 - hours_per_task[list(old_task.keys())[0]]
                }
            elif temp_result[worker_id]['Свободных часов'] < hours_per_task[list(old_task.keys())[0]]:  # Нельзя превышать 8 часов
                continue
            else:
                old_address_is_free = True
                for already_given_tasks in temp_result[worker_id]['Задания']:
                    if already_given_tasks['Адрес'] == created_old_task['Адрес']:
                        old_address_is_free = False  # 1 адрес это 1 задание -> нельзя выдавать его повторно
                        break
                if old_address_is_free:
                    temp_result[worker_id]['Задания'].append(created_old_task)
                    temp_result[worker_id]['Свободных часов'] -= hours_per_task[list(old_task.keys())[0]]


# Строгий блок распределения заданий
def strong_paste_task(available_grade: list[str], dict_with_tasks: dict, name_of_task: str):
    """
    Назначит работникам задачи на день (только работникам поблизости)

    :param available_grade: Массив с грейдами работников которых можно допустить до работы
    :param dict_with_tasks: Словарь, в котором лежат ключи - адреса заданий, значения - ближайшие офисы
    :param name_of_task: Название задания
    """
    global temp_result

    for street, closest_point in dict_with_tasks.items():
        actual_task = {'Задание': name_of_task, 'Адрес': street}  # Создаём задание
        for actual_worker_id, params in workers.items():  # Перебираем доступных работников
            if params['Грейд'] in available_grade and params['Адрес'] == closest_point:  # Если сотрудник подходит по грейду и рядом
                if actual_worker_id not in temp_result:
                    temp_result[actual_worker_id] = {
                        'Задания': [actual_task],
                        'Свободных часов': 8 - hours_per_task[name_of_task]
                    }
                elif temp_result[actual_worker_id]['Свободных часов'] < hours_per_task[name_of_task]:  # Нельзя превышать 8 часов
                    continue
                else:
                    address_is_free = True
                    for task in temp_result[actual_worker_id]['Задания']:
                        if task['Адрес'] == actual_task['Адрес']:
                            address_is_free = False  # 1 адрес это 1 задание -> нельзя выдавать его повторно
                            break
                    if address_is_free:
                        temp_result[actual_worker_id]['Задания'].append(actual_task)
                        temp_result[actual_worker_id]['Свободных часов'] -= hours_per_task[name_of_task]


# Не строгий блок распределения задач
def loyal_paste_task(available_grade: list[str], dict_with_tasks: dict, name_of_task: str):
    """
    Назначит работникам задачи на день (уже несмотря на адрес, просто будет выдавать незанятые задачи всем доступным работникам)

    :param available_grade: Массив с грейдами работников которых можно допустить до работы
    :param dict_with_tasks: Словарь, в котором лежат ключи - адреса заданий, значения - ближайшие офисы
    :param name_of_task: Название задания
    """
    global temp_result

    for street in dict_with_tasks:
        actual_task = {'Задание': name_of_task, 'Адрес': street}  # Создаём задание
        for actual_worker_id, params in workers.items():  # Перебираем доступных работников
            if params['Грейд'] in available_grade:  # Если сотрудник подходит по грейду
                if actual_worker_id not in temp_result:
                    temp_result[actual_worker_id] = {
                        'Задания': [actual_task],
                        'Свободных часов': 8 - hours_per_task[name_of_task]
                    }
                elif temp_result[actual_worker_id]['Свободных часов'] < hours_per_task[name_of_task]:  # Нельзя превышать 8 часов
                    continue
                else:
                    address_is_free = True
                    for task in temp_result[actual_worker_id]['Задания']:
                        if task['Адрес'] == actual_task['Адрес']:
                            address_is_free = False  # 1 адрес это 1 задание -> нельзя выдавать его повторно
                            break
                    if address_is_free:
                        temp_result[actual_worker_id]['Задания'].append(actual_task)
                        temp_result[actual_worker_id]['Свободных часов'] -= hours_per_task[name_of_task]

# TODO: как-то убедиться что в выданных задачах нет дупликатов (имею ввиду, что если я выдал задачу - убери её из списка задач)
# Выдаём задания высокого приоритета
strong_paste_task(
    available_grade=['Синьор'],
    dict_with_tasks=locations_for_first_task["Условие1"],
    name_of_task="Выезд на точку для стимулирования выдач"
)
strong_paste_task(
    available_grade=['Синьор'],
    dict_with_tasks=locations_for_first_task["Условие2"],
    name_of_task="Выезд на точку для стимулирования выдач"
)
loyal_paste_task(
    available_grade=['Синьор'],
    dict_with_tasks=locations_for_first_task["Условие1"],
    name_of_task="Выезд на точку для стимулирования выдач"
)
loyal_paste_task(
    available_grade=['Синьор'],
    dict_with_tasks=locations_for_first_task["Условие2"],
    name_of_task="Выезд на точку для стимулирования выдач"
)
# TODO: убедиться, что нет свободных синьоров при не взятых задачах высокого приоритета


# Выдаём задания среднего приоритета
strong_paste_task(
    available_grade=['Синьор', 'Мидл'],
    dict_with_tasks=locations_for_second_task,
    name_of_task="Обучение агента"
)
loyal_paste_task(
    available_grade=['Синьор', 'Мидл'],
    dict_with_tasks=locations_for_second_task,
    name_of_task="Обучение агента"
)
# TODO: убедиться, что нет свободных синьоров/мидлов при не взятых задачах среднего приоритета


# Выдаём задания низкого приоритета
strong_paste_task(
    available_grade=['Синьор', 'Мидл', 'Джун'],
    dict_with_tasks=locations_for_third_task["Условие1"],
    name_of_task="Доставка карт и материалов"
)
strong_paste_task(
    available_grade=['Синьор', 'Мидл', 'Джун'],
    dict_with_tasks=locations_for_third_task["Условие2"],
    name_of_task="Доставка карт и материалов"
)
loyal_paste_task(
    available_grade=['Синьор', 'Мидл', 'Джун'],
    dict_with_tasks=locations_for_third_task["Условие1"],
    name_of_task="Доставка карт и материалов"
)
loyal_paste_task(
    available_grade=['Синьор', 'Мидл', 'Джун'],
    dict_with_tasks=locations_for_third_task["Условие2"],
    name_of_task="Доставка карт и материалов"
)
# TODO: убедиться, что нет свободных работников при не взятых задачах

# Записываем данные в JMC
for worker_id_key, value_for_worker in temp_result.items():
    write_worker_in_jmc(worker_id_key, value_for_worker['Задания'])
# TODO: экспортировать оставшиеся задачи в ntt
# TODO: exception_catcher - если ошибка, то запи её в логгер
