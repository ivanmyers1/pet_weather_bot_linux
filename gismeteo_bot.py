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

user_data = {}

#  обработка start
@bot.message_handler(commands= ['start'])
def send_greeting(message):
    global user_data
    # get user's id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username
    user_data_updated = {'user_id': user_id,'user_name': user_name, 'username': username}


    #  создаем кнопки для выбора часового пояса
    markup = InlineKeyboardMarkup(row_width=3)  # создание инлайн клавиатуры (3 кнопки в одном ряду)
    buttons = []
    for callback_data, text in clock_time.items():
        buttons.append(InlineKeyboardButton(text=text,callback_data=callback_data))

    markup.add(*buttons)

    bot.send_message(message.chat.id,'Приветствую, я помогу узнать погоду в определенное время или в данный момент!'
                                     '\nВыбери свой часовой пояс. И время когда хочешь получать данные.',
                     reply_markup=markup)

    user_data = user_data_updated
    print(user_data)




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



user_zone = {}
#  обрабатываем часовой пояс и выбираем когда юзер хочет получать данные
@bot.callback_query_handler(func=lambda call: True)
def obrabotka(call):
    global user_zone

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
    user_zone = {'id_tg': call.from_user.id, 'zone': user_number}
    print(user_zone)
        






print("bot's working")
#  запуск сервера
bot.infinity_polling()




