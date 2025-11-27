import requests
import json
from api import weather_api
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()


def get_location_from_bd(id_tg):
    cursor.execute("""
        SELECT location FROM send_location WHERE id_tg = %s
        """, (id_tg,))
    result_location = cursor.fetchone()
    result_location = result_location[0]
    print(f'{id_tg=} ; {result_location=}')
    return result_location


def open_weather_api(user_input):
    api = weather_api
    # city = input('в каком городе хочешь увидеть погоду: ')
    city = user_input
    call = f'http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={api}&units=metric'
    response = requests.get(call).text
    data_dict = json.loads(response)

    return data_dict


def format(id_tg_format):
    user_input = get_location_from_bd(id_tg=id_tg_format)
    dict_ = open_weather_api(user_input)
    get_info = {
        'Описание': dict_.get('weather', [{}])[0].get('description', 'Н/Д'),
        'Температура': dict_.get('main', {}).get('temp', 'Н/Д'),
        'Ощущается как': dict_.get('main', {}).get('feels_like', 'Н/Д'),
        'Влажность': dict_.get('main', {}).get('humidity', 'Н/Д'),
        'Давление': dict_.get('main', {}).get('pressure', 'Н/Д'),
        'Видимость': dict_.get('visibility', 'Н/Д'),
        'Облачность': dict_.get('clouds', {}).get('all', 'Н/Д'),
        'Ветер': {
            'Скорость': dict_.get('wind', {}).get('speed', 'Н/Д'),
            'Направление': dict_.get('wind', {}).get('deg', 'Н/Д'),
            'Порыв': dict_.get('wind', {}).get('gust', 'Н/Д') # конструкция идентична dict_['wind']['gust'] но с дополнительной проверкой на наличие данных
        },

    }
    return get_info


# DRAFT
# def does_location_exist():
#     data = format()
#     # don't have a data
#     if data['Температура'] == 'Н/Д':
#         return False
#     # have a data
#     else:
#         return True



# print(format(901304271))
# print(open_weather_api())

