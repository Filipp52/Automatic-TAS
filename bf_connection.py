"""Файл хранящий функции, которые будут импортированы во фронт и использоваться там"""
import random
import string
import pandas as pd
from background_package.load_xlsx import get_workers
from background_package.work_with_jmc import update_jmc, get_jmc
from settings import path2dataset
import hashlib
from settings import today_date, path2jmc


def get_user_dict(worker_id: str, date=today_date) -> dict:
    """
    Получи словарь работника:

    {
      "ФИО": "Семёнов Семён Иванович",
      "Грейд": "Джун",
      "Кол-во заданий": 2,
      "Исходная локация": "Краснодар, ...",
      "Задания": {
        "Краснодар, ...": {
          "Название задания": "Не выполнено"
        },
        "ул. Уральская, д. 79/1": {
          "Название задания": "Не выполнено"
        }
      }
    }

    :param worker_id: id сотрудника
    :param date: дата форматом 'ГГГГ-ММ-ДД' --- по умолчанию стоит сегодняшняя дата
    :return: словарь работника
    """
    return get_jmc(path2jmc, date, worker_id)


def __get_sha256_hash__(s:  str) -> str:
    """
    Захеширует строку через sha256

    :param s: строка для преобразования
    :return: хэш
    """
    sha256_hash = hashlib.sha256(s.encode()).hexdigest()
    return str(sha256_hash)


def __generate_password__() -> str:
    """
    Функция генерирует случайный пароль длиной 8 символов
    """
    characters = string.ascii_letters + string.digits + string.punctuation + string.ascii_letters
    password = ''.join(random.choice(characters) for _ in range(10))
    return password


def __generate_login__(fio: str) -> str:
    """
    Функция генерирует логин по принципу ФИО (первые буквы) + '_' + 100

    Если такой логин уже есть, то делаем '101' и тд...
    """
    first_letter = fio.split()
    if len(first_letter) != 3:
        raise Exception(f"Ошибка с ФИО сотрудника --- скорее всего что-то с пробелами ('{fio}')")

    before_num = f'{first_letter[0][0]}{first_letter[1][0]}{first_letter[2][0]}_'
    num = 100
    login = before_num + str(num)

    workers_id = pd.read_excel(path2dataset, sheet_name='Справочник сотрудников').loc[:, ['ID']]
    while login in workers_id.values:
        num += 1
        login = before_num + str(num)

    return login


def registrate_new_worker(fio: str, address: str, grad: str) -> dict[str, str]:
    """
    Зарегистрирует нового работника

    :param fio: ФИО через пробел ('Иванов Пётр Олегович')
    :param address: Адрес, где находится сотрудник (Обязательно начнинается с города - 'Краснодар, ...')
    :param grad: Грейд сотрудника ('Синьор', 'Мидл', 'Джун')
    :return: Словарь с параметрами 'Логин' и 'Пароль'
    """
    if grad not in ['Синьор', 'Мидл', 'Джун']:
        raise Exception(f"Ошибка с грейдом нового сотрудника, '{grad}' нельзя использовать")
    # TODO: проверить адрес на пригодность

    workers_list = pd.read_excel(path2dataset, sheet_name='Справочник сотрудников')
    col = list(workers_list.columns)

    worker_pass = __generate_password__()
    worker_login = __generate_login__(fio)

    new_line = pd.DataFrame(
        [
            [worker_login, address, grad, fio, __get_sha256_hash__(worker_pass)]
        ],
        columns=col
    )

    book = pd.read_excel(path2dataset, sheet_name=None)
    book['Справочник сотрудников'] = pd.concat([book['Справочник сотрудников'], new_line], ignore_index=True)

    with pd.ExcelWriter(path2dataset) as writer:
        for sheet, data in book.items():
            data.to_excel(writer, sheet_name=sheet, index=False, header=True)

    return {'Логин': worker_login, 'Пароль': worker_pass}


def login_user(login: str, password: str) -> dict:
    """
    Проверка логина/пароля пользователя

    Если пользователь ввёл всё верно, то я верну:
    {
      "ФИО": "Семёнов Семён Иванович",
      "Грейд": "Джун",
      "Кол-во заданий": 2,
      "Исходная локация": "Краснодар, ...",
      "Задания": {
        "Краснодар, ...": {
          "Название задания": "Не выполнено"
        },
        "ул. Уральская, д. 79/1": {
          "Название задания": "Не выполнено"
        }
      }
    }
    Это на сегодняшнюю дату будет

    :param login: Логин работника
    :param password: Пароль работника
    :return: Словарь если есть работник, Ошибку (KeyError) если нет такого
    """
    input_data = pd.read_excel(path2dataset, sheet_name='Справочник сотрудников').loc[:, ["ID", "Пароль"]]
    input_data = input_data[(input_data['ID'] == login)]
    if len(list(input_data.values)) != 1:
        raise KeyError('Ошибка в логине')
    elif list(input_data.values)[0][1] == __get_sha256_hash__(password):
        return get_user_dict(login)
    else:
        raise KeyError('Ошибка в пароле')


# TODO: функция удаления/изменения работника
# TODO: функция удаления/изменения точки
# TODO: get_all_workers()


def switch_task_status(worker_id: str, name_of_street: str):
    """
    Изменит статус задачи
    'Не выполнено' -> 'Выполнено'
    'Выполнено' -> 'Не выполнено'

    :param worker_id: id работника
    :param name_of_street: улица, на которй он выполнил задание
    """
    worker = get_user_dict(worker_id)
    for name_of_task in worker["Задания"][name_of_street]:
        if worker["Задания"][name_of_street][name_of_task] == 'Не выполнено':
            worker["Задания"][name_of_street][name_of_task] = 'Выполнено'
        else:
            worker["Задания"][name_of_street][name_of_task] = 'Не выполнено'
    update_jmc(actual_key=worker_id, value=worker, way_for_actual_key=f'{today_date}', path_to_jmc=path2jmc)


def get_all_workers() -> list[list[int | str]]:
    """
    Возвращаю список из списков по каждому сотруднику, использую формат:

    [[Порядковый номер, ID, ФИО, Адрес, Грейд], ...]

    :return: список сотрудников
    """
    workers_dict = get_workers(path2dataset)
    result = []
    num_of_worker = 0

    for worker_id, worker_params in workers_dict.items():
        num_of_worker += 1
        worker = [
            num_of_worker,
            worker_id,
            worker_params['ФИО'],
            worker_params['Адрес'],
            worker_params['Грейд']
        ]
        result.append(worker)

    return result
