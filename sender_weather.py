from datetime import datetime,UTC, timedelta
import time
import psycopg2
import telebot
from api import TOKEN
from get_data import format_f
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()

bot = telebot.TeleBot(TOKEN)

send_time = {}
list_of_id = []
def test():

    def moscow_time():
        add_time = timedelta(hours=3)
        utc_time = datetime.now(UTC)
        moscow_time_ = utc_time + add_time
        return moscow_time_.time().strftime('%H:%M')


    def get_send_time_of_the_user():
        cursor.execute('''
        SELECT * FROM send_time;
        ''')
        result = cursor.fetchall()
        # наполняем send time данными из кортежа
        for key, value in result:
            send_time[key] = value
            list_of_id.append(key)
        send_time.update(send_time)

        return list_of_id,send_time


    def checker():
        chars = []
        for id_ in list_of_id:
            for value in send_time[id_]:
                chars.append(value)
            value = ''.join(chars)
            def split_value():
                block_size = 5
                #print(value)
                for num in range(len(value)):
                    window = value[num:num+block_size]
                    try:
                        if datetime.strptime(window, '%H:%M'):
                            # проверка если сейчас времени столько сколько в таблице то отправить данные
                            # print(f'{id_=} {window=} {moscow_time()}')
                            if window == moscow_time():
                                print(f'sending data to {id_}, time: {moscow_time()}')
                                bot.send_message(chat_id=id_,text=f'{format_f(id_)}')
                                continue
                            else:
                                print('no users for send')
                                continue


                    except ValueError:
                        continue


            split_value()
            #print(id, value)
            chars.clear()



    list_of_id.clear()
    get_send_time_of_the_user()
    checker()

# test()

while True:
    print(datetime.now())
    test()
    time.sleep(60.0)


