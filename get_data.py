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

def format_deg(deg):
    text = ['Северо-западное направление', 'Северное направление', 'Северо-восточное направление',
            'Восточное направление', 'Юго-восточное направление', 'Южное направление', 'Юго-западное направление',
            'Западное направление','Северо-западное направление']
    direct = [285,345]
    interval = [60, 30]
    for num in range(1,9):
        if num % 2 == 0:
            direct[0] = direct[0] + interval[1]
            direct[1] = direct[1] + interval[0]

        else:
            direct[0] = direct[0] + interval[0]
            direct[1] = direct[1] + interval[1]

        for n in range(len(direct)):
            if direct[n] > 360:
                direct[n] -= 360
        # print(direct)

        for n in range(direct[0], direct[1]+1):
            if deg == n:
                # print(text[num])
                return text[num]
            elif 346 <= deg <= 360 or 0 <= deg <=14:
                # print(text[1])
                return text[1]
    return None

def recomendation_by_weather(temp,wind,humidity,description):
    # wind = float(wind)
    recommendetion = 'Рекомендаций нет'
    if 2 >= temp > -7 and description == 'дождь' or 1 >= temp < 0 and humidity > 87:
        recommendetion = 'На асфальте и тротуарах может образовываться гололедица. Наденьте обувь с грубой, нескользящей подошвой.'
    elif description == 'дождь' and wind >= 10:
        recommendetion = 'На улице сильный ветер. Откажитесь от зонта в пользу дождевика с капюшоном.'
    elif 14.0 >= temp >= 6.0 and humidity > 83.0 and description == 'пасмурно' and wind > 4.2:
        recommendetion = 'Высокая влажность с умеренным ветром, воздух может быть пронизывающим. Одежда из синтетики будет комфортнее хлопка.'
    elif temp >= 25.0 and humidity > 77.0 and (description == 'ясно' or description == 'переменная облачность' ) and wind < 2.8:
        recommendetion = 'Сегодня жарко и душно. Вода и головной убор точно не помешают.'
    elif wind > 5.7 and 10.0 >= temp >= -1.0:
        recommendetion = 'Сильный ветер может продувать. Наденьте ветрозащитный слой, закройте уши и горло '
    elif temp > 0 and description == 'снег':
        recommendetion = 'Сегодня мокрый снег. Наденьте водоотталкивающую обувь и одежду.'

    return recommendetion


def format_f(id_tg_format):
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


    formated_sentence = (f'Здравствуйте, сейчас {get_info["Описание"]}.\nТемпература: {round(get_info["Температура"])}°C\n'
                         f'Ощущается как {round(get_info["Ощущается как"])}°C\nВлажность {get_info["Влажность"]}%\n'
                         f'Облачность {get_info["Облачность"]}%\n'
                         f'Ветер {round(get_info["Ветер"]["Скорость"],1)} м/с {format_deg(get_info["Ветер"]["Направление"])}\n'
                         f'{recomendation_by_weather(temp=get_info["Температура"], humidity=get_info["Влажность"], wind=get_info["Ветер"]["Скорость"],
                                                     description=get_info["Описание"])}')
    return formated_sentence


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

