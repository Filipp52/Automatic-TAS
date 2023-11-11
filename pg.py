from background_package.load_xlsx import high_1, high_2, low_1, low_2, get_workers, middle_1
import pandas as pd
from background_package.work_with_jmc import get_jmc, write_worker_in_jmc
from settings import path2dataset, path2jmc, path2ntt, today_date, yesterday_date
import json


def create_upload_tasks():
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
        **high_1(data_about_locations, seniors_offices),
        **high_2(data_about_locations, seniors_offices)
    }
    locations_for_second_task = middle_1(data_about_locations, seniors_a_midl_offices)
    locations_for_third_task = {
        **low_1(data_about_locations, all_offices),
        **low_2(data_about_locations, all_offices)
    }
    d = {
        "Выезд на точку для стимулирования выдач": [],
        "Обучение агента": [],
        "Доставка карт и материалов": []
    }
    for k in locations_for_first_task:
        d["Выезд на точку для стимулирования выдач"].append(k)
    for k in locations_for_second_task:
        d["Обучение агента"].append(k)
    for k in locations_for_third_task:
        d["Доставка карт и материалов"].append(k)
    print(d)
    with open("tasks.txt", "w") as t:
        for k in d:
            for v in d[k]:
                t.write(f"{k}: {v}\n")
    with open("tasks.json", "w") as t:
        json.dump(d, t, ensure_ascii=False)


def sync():
    with open("tasks.json", "r") as t:
        d = json.load(t)

    for i in d['Выезд на точку для стимулирования выдач']:
        for j in d['Обучение агента']:
            if i == j:
                print(f"'{i}' находится в 'Выезд на точку для стимулирования выдач' и 'Обучение агента'")
        for k in d['Доставка карт и материалов']:
            if i == k:
                print(f"'{i}' находится в массивах 'Выезд на точку для стимулирования выдач' и 'Доставка карт и материалов'")

    for j in d['Обучение агента']:
        for k in d['Доставка карт и материалов']:
            if j == k:
                print(f"'{j}' находится в массивах 'Обучение агента' и 'Доставка карт и материалов'")


def setter():
    with open("tasks.json", "r") as t:
        d = json.load(t)

    for k, v in d.items():
        if len(v) != len(set(v)):
            print(k, len(v) - len(set(v)), sep=" : ")


def clean_xlsx(sheet_name: str, label_to_del_name: str | None = None):  # Не работает
    workers_list = pd.read_excel(path2dataset, sheet_name=None)

    ac_in = 0
    for value in workers_list[sheet_name].values:
        if str(value[0]) == 'nan':
            workers_list[sheet_name].drop([ac_in], inplace=True)
        ac_in += 1

    if label_to_del_name:
        workers_list[sheet_name] = workers_list[sheet_name].drop(labels=[label_to_del_name], axis=1)

    with pd.ExcelWriter(path2dataset) as writer:
        for sheet, data in workers_list.items():
            data.to_excel(writer, sheet_name=sheet, index=False, header=True)


clean_xlsx('Входные данные для анализа')
