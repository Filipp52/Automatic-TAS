from flask import Flask, render_template, request
import bf_connection
import json
from settings import path2jmc, path2ntt


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'root' and password == 'pass':
            return render_template('admin_main.html', result=parse_task_for_today())
        else:
            message = "Неверный логин или пароль"
            return render_template('login_form.html', message=message)
    else:
        return render_template('login_form.html')


@app.route('/admin/home')
def admin_home():
    return render_template('admin_main.html', result=parse_task_for_today())


@app.route('/admin/tasks', methods=['POST', 'GET'])
def admin_tasks():
    message = ''
    if request.method == 'POST':
        address = request.form.get('address')
        date = request.form.get('date')
        ordered = request.form.get('ordered')
        days = request.form.get('days')
        applications = request.form.get('applications')
        cards = request.form.get('cards')
        bf_connection.registrate_new_location(address, date, ordered, int(days), int(applications), int(cards))
    return render_template('admin_tasks.html', result=parse_task_for_today() + parse_not_taken_task(), message=message)


@app.route('/admin/staff', methods=['POST', 'GET'])
def admin_staff():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        grade = request.form.get('grade')
        bf_connection.registrate_new_worker(name, address, grade)
    return render_template('admin_staff.html', result=bf_connection.get_all_workers())


@app.route('/admin/about_task', methods=['POST', 'GET'])
def admin_about_task():
    task_info = ''
    if request.method == 'POST':
        search = request.form.get('search')

        # Получить информацию о задаче (по ее адресу)
        task_info = None
    return render_template('admin_about_task.html', result=task_info)


def parse_task_for_today():
    with open(path2jmc, encoding='utf-8') as json_file:
        data = json.load(json_file)
        date = list(data.keys())[0]
        ids = list(data[date].keys())
        tasks = []
        ind = 0
        # N Address Task Surname Status
        for i in range(len(ids)):
            for address in data[date][ids[i]]['Задания'].keys():
                task = list(data[date][ids[i]]['Задания'][address].keys())[0]
                ind += 1
                tasks.append(
                    [ind, address, task,  data[date][ids[i]]['Задания'][address][task],
                     data[date][ids[i]]['ФИО'], ids[i]])
        return tasks


def parse_not_taken_task():
    with open(path2ntt, encoding='utf-8') as json_file:
        data = json.load(json_file)
        del data['Дата']
        tasks = []
        ind = len(parse_task_for_today()) + 1
        for value, keys in data.items():
            for key in keys:
                tasks.append([ind, value, key, '-', 'Не назначено'])
                ind += 1
        return tasks


@app.route('/admin/delete_task/')
def delete_task():
    # del_taken_task()
    return admin_tasks()


if __name__ == '__main__':
    all_tasks = bf_connection.get_all_locations()

    app.run()
