"""В этом файле функции для работы с JsonMemoryCommunication"""
import json
from background_package.load_xlsx import get_workers
from settings import month_date, path2dataset, path2jmc, today_date


jmc_example = {
    "ГГГГ-ММ-ДД (дата)": {
        "ID_работника (ФИО_трёхзначное число)": {
            "ФИО": "ФИО",
            "Грейд": "грейд",
            "Кол-во заданий": "число заданий на день (кол-во элементов массивов в разделе задания)",
            "Исходная локация": "изначальное местоположение работника",
            "Задания (ключи словаря расставлены в нужной последовательности)": {
                "Адрес1": {"Название задания 1": "Статус"},
                "Адрес2": {"Название задания 1": "Выполнено/Не выполнено"}
            }
        }
    },
    "2023-11-08": {
        "ДНВ_123": {
            "ФИО": "Дерягин Никита Владимирович",
            "Грейд": "Синьор",
            "Кол-во заданий": 3,
            "Исходная локация": "Краснодар, Красная, д. 139",
            "Задания": {
                "ул. Красная, д. 149": {"Выезд на точку для стимулирования выдач": "Не выполнено"},
                "ул. им. Селезнева, д. 197/5": {"Обучение агента": "Не выполнено"},
                "ул. им. Героя Аверкиева А.А., д. 8": {"Обучение агента": "Выполнено"}
            }
        },
        "ИАФ_321": {
            "ФИО": "Иванов Адам Федорович",
            "Грейд": "Мидл",
            "Кол-во заданий": 2,
            "Исходная локация": "Краснодар, В.Н. Мачуги, 41",
            "Задания": {
                "ул. Северная, д. 389": {"Выезд на точку для стимулирования выдач": "Не выполнено"},
                "ул. Красных Партизан, д. 439": {"Выезд на точку для стимулирования выдач": "Не выполнено"}
            }
        }
    },
    "2023-11-07": {
        "ДНВ_123": {
            "ФИО": "Дерягин Никита Владимирович",
            "Грейд": "Синьор",
            "Кол-во заданий": 2,
            "Исходная локация": "Краснодар, Красная, д. 139",
            "Задания": {
                "ул. Уральская, д. 162": {"Выезд на точку для стимулирования выдач": "Выполнено"},
                "ул. Коммунаров, д. 258": {"Обучение агента": "Выполнено"}
            }
        },
        "ИАФ_321": {
            "ФИО": "Иванов Адам Федорович",
            "Грейд": "Мидл",
            "Кол-во заданий": 2,
            "Исходная локация": "Краснодар, В.Н. Мачуги, 41",
            "Задания": {
                "ул. Северная, д. 389": {"Выезд на точку для стимулирования выдач": "Выполнено"},
                "ул. Уральская, д. 79/1": {"Выезд на точку для стимулирования выдач": "Выполнено"}
            }
        }
    }
}


def get_jmc(path_to_jmc: str, *key: str) -> dict:
    """
    Получите словарь скачанный из JsonMemoryCommunication

    :param path_to_jmc: путь, где хранится файл jmc
    :param key: если хочешь получить не все значения, а конкретные, то передавай ключи по которым мне нужно идти
    :return: словарь jmc
    """
    with open(path_to_jmc, "r") as jmc_file:
        jmc_actual_key = json.load(jmc_file)
        for k in key:
            jmc_actual_key = jmc_actual_key[k]
        return jmc_actual_key


def rewrite_jmc(pat_to_jmc: str, jmc: dict):
    """
    Записывает ваш словарь в JsonMemoryCommunication

    :param pat_to_jmc: путь, где хранится файл jmc
    :param jmc: словарь, который нужно записать
    """
    with open(pat_to_jmc, "w") as jmc_file:
        json.dump(jmc, jmc_file, ensure_ascii=False)


def update_jmc(actual_key: str, value, path_to_jmc: str, way_for_actual_key: str | None = None):
    """
    Обновляет JsonMemoryCommunication

    :param actual_key: ключ, на который мы запишем переданные значения
    :param value: значение, которое нужно записать
    :param path_to_jmc: путь где хранится файл jmc
    :param way_for_actual_key: Если вдруг вы хотите поместить новое значение не в корень jmc то передайте путь ключей, используя '/'
    """
    jmc = get_jmc(path_to_jmc)
    try:
        del jmc[month_date]
    except KeyError:
        pass
    try:
        jmc[today_date]
    except KeyError:
        jmc[today_date] = {}
    if way_for_actual_key:
        all_jmc = jmc.copy()
        for k in way_for_actual_key.split("/"):
            jmc = jmc[k]
        jmc[actual_key] = value

        keys = way_for_actual_key.split("/")
        i = len(keys)
        temp = {}
        while i > 0:
            i -= 1
            temp[keys[i]] = jmc
            jmc = temp
            temp = {}

        all_jmc[list(jmc.keys())[0]] = list(jmc.values())[0]
        jmc = all_jmc.copy()
    else:
        jmc[actual_key] = value
    rewrite_jmc(path_to_jmc, jmc)


def write_worker_in_jmc(worker_id: str, tasks: list[dict[str, str]]):
    """
    Записывает задачи работника на сегодняшний день

    :param worker_id: ID работника
    :param tasks: Массив с словарями (задачами)
    """
    try:
        worker_params = get_workers(path_to_dataset=path2dataset)[worker_id]
    except KeyError:
        raise KeyError(f"Работника с ID - '{worker_id}' нет в ДатаСете")

    result = {
        "ФИО": worker_params['ФИО'],
        "Грейд": worker_params['Грейд'],
        "Кол-во заданий": 0,
        "Исходная локация": worker_params['Адрес'],
        "Задания": {}
    }

    for task in tasks:
        result["Задания"][task['Адрес']] = {task['Задание']: 'Не выполнено'}
        result["Кол-во заданий"] += 1

    update_jmc(
        actual_key=worker_id,
        value=result,
        path_to_jmc=path2jmc,
        way_for_actual_key=f'{today_date}'
    )
