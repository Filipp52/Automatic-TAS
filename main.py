from flask import Flask, render_template
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('admin_main.html', result=new_table)


@app.route('/home')
def tasks():
    return render_template('admin_tasks.html')


@app.route('/staff')
def staff():
    return render_template('admin_staff.html')


if __name__ == '__main__':
    with open('jmc_example.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        # Today is
        date = list(data.keys())[0]
        count = 1
        ids = list(data[date].keys())
        
        new_table = []
        # N Adress Task Surname Status
        for i in range(len(ids)):
            adresses = data[date][ids[i]]['Задания'].keys()
            for adress in adresses:
                tmp = []
                tmp.append(count)
                tmp.append(adress)
                task = list(data[date][ids[i]]['Задания'][adress].keys())[0]
                tmp.append(task)
                tmp.append(data[date][ids[i]]['ФИО'])
                tmp.append(data[date][ids[i]]['Задания'][adress][task])
                new_table.append(tmp)
                count += 1
        data["2023-11-08"]["ДНВ_123"]['Задания']["ул. Красная, д. 149"][
            "Выезд на точку для стимулирования выдач"] = 'Done'
        
        print(new_table)
    app.run(debug=True)
