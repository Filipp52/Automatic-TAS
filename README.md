# Automatic-TAS
***
# Файлы:
### JMC - json объект (JsonMemoryCommunicate)
###### Импровизированная база данных (за последние 30 дней)
* Корневые ключи - даты (ГГГГ-ММ-ДД)
* Подключи (на каждый день) - id выездного сотрудника
* На каждом сотруднике есть свой словарь со структурой:
> ФИО
> 
> Грейд
> 
> Кол-во заданий
> 
> Исходная локация
> 
> Задания
>> Адрес задания : {Название задания : Статус}
###### Например:
```json
{"2023-11-07": 
  {"ДНВ_123": {
    "ФИО": "Дерягин Никита Владимирович", 
    "Грейд": "Синьор", 
    "Кол-во заданий": 2, 
    "Исходная локация": "Краснодар, Красная, д. 139", 
    "Задания": {
      "ул. Уральская, д. 162": {"Выезд на точку для стимулирования выдач": "Выполнено"}, 
      "ул. Коммунаров, д. 258": {"Обучение агента": "Не выполнено"}
      }
    }
  }
}
```
#
### NTT - json объект (NotTakenTasks)
###### Файл хранящий не взятые задачи только на актуальную дату
* Ключи - Адреса
* Значения - Массив с названиями заданий
###### Например:
```json
{
  "ул. Уральская, д. 162": ["Выезд на точку для стимулирования выдач"], 
  "ул. Красных Партизан, д. 117": ["Обучение агента", "Доставка карт и материалов"], 
  "ул. Таманская, д. 153 к. 3, кв. 2": ["Обучение агента"],
}
```
***