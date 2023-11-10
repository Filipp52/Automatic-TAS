"""В этом фаул функции для работы с NotTakenTasks"""
import json


ntt_example = {
    "Дата": "2023-11-10",
    "ул. Уральская, д. 162": ["Выезд на точку для стимулирования выдач"],
    "ул. Красных Партизан, д. 117": ["Обучение агента", "Доставка карт и материалов"],
    "ул. Таманская, д. 153 к. 3, кв. 2": ["Обучение агента"],
}


def get_ntt(path_to_ntt: str, *key: str) -> dict[str, list[str]]:
    """
    Получите словарь скачанный из NotTakenTasks

    :param path_to_ntt: путь, где хранится файл ntt
    :param key: если хочешь получить не все значения, а конкретные, то передавай ключи по которым мне нужно идти
    :return: словарь ntt
    """
    with open(path_to_ntt, "r") as ntt_file:
        ntt_actual_key = json.load(ntt_file)
        for k in key:
            ntt_actual_key = ntt_actual_key[k]
        return ntt_actual_key


def rewrite_ntt(path_to_ntt: str, ntt: dict):
    """
    Записывает ваш словарь в NotTakenTasks

    :param path_to_ntt: путь, где хранится файл ntt
    :param ntt: словарь, который нужно записать
    """
    with open(path_to_ntt, "w") as ntt_file:
        json.dump(ntt, ntt_file, ensure_ascii=False)
