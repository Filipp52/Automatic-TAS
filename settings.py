"""В этом файле все изменяемы параметры"""
import os
from datetime import datetime, timedelta
import pytz


def check_file(path: str):
    if not os.path.isfile(path):
        raise Exception(f"I can't find file: {path}")


corner_dir = os.getcwd()
now_moscow = datetime.now(pytz.utc).astimezone(
    pytz.timezone('Europe/Moscow')
)
yesterday = now_moscow - timedelta(days=1)  # Вопрос, будут ли изменяться эти данные на сервере когда в 00:00 мы перезапустимся?
month = now_moscow - timedelta(days=30)
os.makedirs(os.path.join(corner_dir, 'datas'), exist_ok=True)


path2dataset = os.path.join(corner_dir, 'datas', 'DataSet.xlsx')
path2jmc = os.path.join(corner_dir, 'datas', 'jmc.json')
path2ntt = os.path.join(corner_dir, 'datas', 'ntt.json')
path2pgc = os.path.join(corner_dir, 'datas', 'pgc.pickle')

check_file(path2dataset)
check_file(path2jmc)
check_file(path2ntt)
check_file(path2pgc)

today_date = str(now_moscow.strftime('%Y-%m-%d'))  # TODO: переписать в функцию актуального дня
yesterday_date = str(yesterday.strftime("%Y-%m-%d"))
month_date = str(month.strftime("%Y-%m-%d"))
