"""В этом файле все изменяемы параметры"""
import os
from datetime import datetime, timedelta
import pytz


def check_file(path: str):
    if not os.path.isfile(path):
        raise Exception(f"I can't find file: {path}")


corner_dir = os.getcwd()
os.makedirs(os.path.join(corner_dir, 'datas'), exist_ok=True)


path2dataset = os.path.join(corner_dir, 'datas', 'DataSet.xlsx')
path2jmc = os.path.join(corner_dir, 'datas', 'jmc.json')
path2ntt = os.path.join(corner_dir, 'datas', 'ntt.json')
path2pgc = os.path.join(corner_dir, 'datas', 'pgc.pickle')

check_file(path2dataset)
check_file(path2jmc)
check_file(path2ntt)
check_file(path2pgc)


def get_msc_date(time_delta=0) -> str:
    """
    Получи дату по москве (по дефолту возращает сегодняшнюю)

    :param time_delta: Сколько дней нужно вычесть из актуального дня
    :return: Строку даты форматом 'ГГГГ-ММ-ДД'
    """
    now_moscow = datetime.now(pytz.utc).astimezone(
        pytz.timezone('Europe/Moscow')
    )
    temp_date = now_moscow - timedelta(days=time_delta)
    return str(temp_date.strftime('%Y-%m-%d'))
