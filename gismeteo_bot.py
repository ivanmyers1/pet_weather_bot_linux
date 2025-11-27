# pip install psycopg2-binary
import time

import json
import requests
from bs4 import BeautifulSoup
from api import weather_api

import psycopg2
import telebot
from datetime import datetime, UTC, timedelta

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# import  buttons
from buttons import clock_time, menu_dict, confirm_button
# import token
from api import TOKEN
import asyncio

bot = telebot.TeleBot(TOKEN)

# work with BD
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()


#  обработка start
@bot.message_handler(commands= ['start'])
def send_greeting(message):
    # создаем кнопки для выбора часового пояса
    markup = InlineKeyboardMarkup(row_width=3)  # создание инлайн клавиатуры (3 кнопки в одном ряду)
    buttons = []
    for callback_data, text in clock_time.items():
        buttons.append(InlineKeyboardButton(text=text,callback_data=callback_data))

    markup.add(*buttons)

    bot.send_message(message.chat.id,'Приветствую, я помогу узнать погоду в определенное время или в данный момент!'
                                     '\nВыбери свой часовой пояс. И время когда хочешь получать данные.',
                     reply_markup=markup)


#  получаем время (только час)
def time_now_f():
    current_time = datetime.now() #  2025-06-30 17:09:28.853964
    time_now = current_time.time() #  17:09:28.853964
    time_hour = time_now.hour # 17
    time_minute = time_now.minute #  09
    if time_minute <= 9:
        time_minute = "0"+ str(time_minute)

    return time_hour, time_minute #  возвращаем кортеж с часом и минутами

# здесь надо дописать логику, если часовой пояс был выбран то пользователь может использзовать команду menu и инфа о времени
# будет браться оттуда сюда, а не из функции start
@bot.message_handler(commands= ['menu'])
def menu_buttons(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for button_text, but_data in menu_dict.items():
        if but_data['type'] == 'callback':
            markup.add(InlineKeyboardButton(button_text, callback_data=but_data['data']))
        elif but_data['type'] == 'url':
            markup.add(InlineKeyboardButton(button_text, url=but_data['data']))
    bot.send_message(call.message.chat.id, text='Меню:', reply_markup=markup)



#  обрабатываем часовой пояс и выбираем когда юзер хочет получать данные
@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def obrabotka(call):

    time = time_now_f() #  получаем кортеж с часом и минутой (время мск)
    result_time_user = time[0]

    user_number = int(call.data)
    result_time_user = user_number + time[0]  # передаем значение часа через кортеж
    if result_time_user >= 24:
        if result_time_user == 24:
            result_time_user = 0
        else:
            result_time_user -= 24  # если у юзера ночь, то переводим время за 12
    bot.answer_callback_query(call.id, text="Часовой пояс успешно выбран!")  # всплывающее уведомление
    minute = time_now_f()[1]
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f'Часовой пояс выбран, у вас сейчас {result_time_user}:{minute}',  # редактируем сообщение
        reply_markup=None)  # убираем клаву инлайн

    menu_buttons(call=call)

    user_id = call.from_user.id
    user_name = call.from_user.first_name
    username = call.from_user.username
    user_data = {'user_id': user_id, 'user_name': user_name, 'username': username}

    user_zone = {'id_tg': call.from_user.id, 'zone': user_number}
    print(user_data, user_zone)
    add_info_about_user_to_tables(user_data=user_data,user_zone=user_zone)
        

def add_info_about_user_to_tables(user_data,user_zone):
    cursor.execute("""
    SELECT 1 FROM users WHERE id_tg = %s
    """, (user_data['user_id'],))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("""
        INSERT INTO users (id_tg,name,user_name) VALUES(%s,%s,%s)
        """,(user_data['user_id'], user_data['user_name'], user_data['username']))
        conn.commit()

        cursor.execute("""
            INSERT INTO time_zone (id_tg,zone_code) VALUES(%s,%s)
            """, (user_zone['id_tg'], user_zone['zone']))
        conn.commit()

    else:
        cursor.execute("""
        UPDATE users SET name=%s, user_name=%s where id_tg=%s 
        """, (user_data['user_name'], user_data['username'], user_data['user_id']))
        conn.commit()

        cursor.execute("""
        UPDATE time_zone SET zone_code=%s where id_tg=%s 
        """, (user_zone['zone'], user_zone['id_tg']))
        conn.commit()

@bot.callback_query_handler(func=lambda call: call.data == "menu_time")
def handle_time(call):

    bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text='Напишите время когда хотели бы получать данные.\n\nНапример: 07:05,12:05,13:30, 15:50, 00:00, 03:10'
    )





test_dict = {}
location_dict = {}
@bot.message_handler(content_types=['text'])
def handle_text(message):

    message_text = message.text
    id_tg_ = message.chat.id

    # проверка на ввод времени
    def filter_time(text):
        able_chars = []
        for n in range(0, 10):
            able_chars.append(str(n))
        able_chars.append(":")
        # print(able_chars)

        filtred_chars = []
        for n in text:
            if n in able_chars:
                filtred_chars.append(n)
        filter_time_text = ''.join(filtred_chars)
        #print(filter_time_text)
        return filter_time_text


    def get_time():
        data_text = filter_time(text=message_text)
        is_time = False
        time_ = []  # ['07:05', '12:05', '13:30']
        block_size = 4

        for n in range(len(data_text) - block_size):
            window_check = data_text[n:n + block_size + 1]

            # проверка на читаемость времени
            try:
                if datetime.strptime(window_check, '%H:%M'):
                    time_.append(window_check)
                    is_time = True

            except ValueError:
                continue

        return time_, is_time

    send_time = get_time()[0]
    # print(f"Пользователь написал время отправки: {get_time()[0]}")


    # проверка на ввод города
    def is_it_city():
        def open_weather_api():
            api = weather_api
            city = str(message_text)
            call_ = f'http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={api}&units=metric'
            response = requests.get(call_).text
            data_dict = json.loads(response)

            return data_dict, city

        def format():
            data = open_weather_api()
            dict_ = data[0]
            city = data[1]
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
                    'Порыв': dict_.get('wind', {}).get('gust', 'Н/Д')
                    # конструкция идентична dict_['wind']['gust'] но с дополнительной проверкой на наличие данных
                },

            }
            return get_info, city

        def does_location_exist():
            data_dict = format()[0]
            city_send = format()[1]
            # don't have a data
            if data_dict['Температура'] == 'Н/Д':
                return False, city_send
            # have a data
            else:
                return True, city_send

        # запуск всех функций проверки
        return does_location_exist()

    # пользователь написал верное время
    if get_time()[1]:
        markup = InlineKeyboardMarkup(row_width=1)
        for button_text, but_data in confirm_button.items():
                markup.add(InlineKeyboardButton(button_text, callback_data=but_data))

        bot.send_message(
            chat_id=message.chat.id,
            text=f'Подтвердите выбраное время: {get_time()[0]}\nИли если что-то не вывелось, напишите еще раз в правильном формате',
            reply_markup=markup
        )

    # пользователь написал время неправильно
    elif not get_time()[1]:
        location_data = is_it_city()

        # если введен город
        if location_data[0]:
            city = location_data[1]

            # если данных города не существует то добавим в таблицу, в противном случае изменим
            cursor.execute("""
                SELECT 1 FROM send_location WHERE id_tg = %s
                """, (id_tg_,))
            result = cursor.fetchone()

            if result is None:
                cursor.execute("""
                        INSERT INTO send_location (id_tg, location) VALUES(%s,%s)
                        """, (id_tg_, city))
                conn.commit()

            else:
                cursor.execute("""
                        UPDATE send_location SET location=%s where id_tg=%s 
                        """, (city, id_tg_))
                conn.commit()



            print(id_tg_, city )

        else:
            bot.send_message(chat_id=message.chat.id,
            text='К сожалению нет такого местоположения с данными'
                             )

        bot.send_message(
            chat_id=message.chat.id,
            text='Извините я вас не понимаю. Мой создатель не наделил меня способностью поддерживать диалог.\n'
                 'Если Вы хотели выбрать время отправки, то его следует писать полностью.\n\n'
                 'Например: 07:10, 12:30, 23:59, 00:00'
        )
    # обновление словаря
    test_dict[message.from_user.id] = send_time



# добавление времени в БД
@bot.callback_query_handler(func=lambda call: call.data == "confirm_button_access")
def handler_confirm_button(call):
    id_tg = call.from_user.id
    send_time = test_dict[id_tg]

    def success_message():
        sep = '--'
        text = []
        n = 6

        # text filling
        def filling_dict():
            for num in range(n):
                if num + 1 == n:
                    text.append(sep)
                    text.append(str(num))
                    text.append(sep)
                    break

                if num != n:
                    text.append(sep)
                    text.append(str(num))
            text.reverse()
            text_ = ''.join(text)
            return text_

        func_text = filling_dict()

        def window_slider(text_=None):
            if text_ is None:
                text_ = func_text
            block_size = 5
            for num in range(len(text_) - 4):
                bot.edit_message_text(chat_id=id_tg, message_id=call.message.message_id,
                                      text=f'Время было успешно добавлено.({text_[num:num + block_size]})')
                time.sleep(0.25)

            bot.delete_message(chat_id=id_tg, message_id=call.message.message_id)
            menu_buttons(call=call)

        # start the function
        window_slider()



    cursor.execute("""
        SELECT 1 FROM send_time WHERE id_tg = %s
        """, (id_tg,))
    result = cursor.fetchone()

    if result is None:
        #print(f'we are into handler conf but {id_tg, send_time}')
        cursor.execute('''
        INSERT INTO send_time(id_tg, send_time) VALUES(%s,%s)
        ''', (id_tg, send_time))
        conn.commit()
        success_message()
        print('information was send')

    elif result is not None: # result == (1,)
        cursor.execute("""
                UPDATE send_time SET send_time=%s where id_tg=%s
                """, (send_time,id_tg))
        conn.commit()
        success_message()
        print(f'information was update, time is {send_time}')



# добавление места в БД
@bot.callback_query_handler(func=lambda call: call.data == "menu_location")
def handler_choose_location(call):
    id_tg_ = call.from_user.id

    bot.edit_message_text(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        text= 'Введите место о котором хотели бы получать информацию. '
    )
    message_text = call
    def location(text=message_text):
        def open_weather_api():
            api = weather_api
            city = str(input('в каком городе хочешь увидеть погоду: '))
            call_ = f'http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={api}&units=metric'
            response = requests.get(call_).text
            data_dict = json.loads(response)

            return data_dict, city

        def format():
            # dict_ = dict({'coord': {'lon': 33.2799, 'lat': 60.4915}, 'weather': [{'id': 804, 'main': 'Clouds', 'description': 'пасмурно', 'icon': '04n'}], 'base': 'stations', 'main': {'temp': 0.63, 'feels_like': -3.06, 'temp_min': 0.63, 'temp_max': 0.63, 'pressure': 1016, 'humidity': 96, 'sea_level': 1016, 'grnd_level': 1014}, 'visibility': 10000, 'wind': {'speed': 3.38, 'deg': 204, 'gust': 9.4}, 'clouds': {'all': 100}, 'dt': 1763918600, 'sys': {'country': 'RU', 'sunrise': 1763878078, 'sunset': 1763902738}, 'timezone': 10800, 'id': 534560, 'name': 'Рекиничи', 'cod': 200})
            dict_ = open_weather_api()[0]
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
                    'Порыв': dict_.get('wind', {}).get('gust', 'Н/Д')
                    # конструкция идентична dict_['wind']['gust'] но с дополнительной проверкой на наличие данных
                },

            }
            return get_info

        def does_location_exist():
            data = format()
            # don't have a data
            if data['Температура'] == 'Н/Д':
                return False
            # have a data
            else:
                return True

        def add_location_to_bd(location_=open_weather_api()[1], id_tg= id_tg_, does_exist=does_location_exist()):
            if does_exist:
                print(id_tg, location_)
                # cursor.execute('''
                # INSERT INTO send_location(id_tg, location) VALUES(%s,%s)
                # ''', (id_tg, location_))

                # нужно добавить изменение

        def filter_location():
            return text

        return filter_location()

    print(location())


print("bot's working")
#  запуск сервера
bot.infinity_polling()


