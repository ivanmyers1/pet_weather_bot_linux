# pip install psycopg2-binary
import psycopg2
import telebot
import datetime
from telebot.types import (InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton, ReplyKeyboardRemove,
                           ReplyKeyboardMarkup)  # кнопки для ответа
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# import  buttons
from buttons import clock_time, choose_dict, menu_dict
# import token
from api import TOKEN

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
    current_time = datetime.datetime.now() #  2025-06-30 17:09:28.853964
    time_now = current_time.time() #  17:09:28.853964
    time_hour = time_now.hour # 17
    time_minute = time_now.minute #  09
    if time_minute <= 9:
        time_minute = "0"+ str(time_minute)

    return time_hour, time_minute #  возвращаем кортеж с часом и минутами


def menu_buttons(call):
    markup = InlineKeyboardMarkup(row_width=1)
    for button_text, but_data in menu_dict.items():
        if but_data['type'] == 'callback':
            markup.add(InlineKeyboardButton(button_text, callback_data=but_data['data']))
        elif but_data['type'] == 'url':
            markup.add(InlineKeyboardButton(button_text, url=but_data['data']))
    bot.send_message(call.message.chat.id, text='Меню:', reply_markup=markup)




#  обрабатываем часовой пояс и выбираем когда юзер хочет получать данные
@bot.callback_query_handler(func=lambda call: True)
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
        text=f'Отлично, у вас сейчас {result_time_user}:{minute}',  # редактируем сообщение
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



print("bot's working")
#  запуск сервера
bot.infinity_polling()


