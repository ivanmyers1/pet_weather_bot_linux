# pip install psycopg2-binary
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()


def create_table_only_one_time():
    # CREATE TABLE users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        id_tg INTEGER NOT NULL UNIQUE,
        name VARCHAR(150),
        user_name VARCHAR(100))
    """)
    # CREATE TABLE time_zone
    cursor.execute("""
    CREATE TABLE time_zone(
    id SERIAL PRIMARY KEY,
    id_tg INTEGER REFERENCES users(id_tg) NOT NULL,
    zone_code INTEGER NOT NULL)
    
    
    """)
    conn.commit()

create_table_only_one_time()

def add_info_to_tables(table,id_tg,name,user_name, zone):
    if table == 1 or table == 3:
        cursor.execute("""
        INSERT INTO users(id_tg, name, user_name) VALUES(%s,%s,%s)
        """, (id_tg,f'{name}',f'{user_name}'))
    if table == 2 or table == 3:
        cursor.execute("""
        INSERT INTO time_zone(id_tg, zone_code) VALUES(%s,%s)
        """, (id_tg,zone))
    conn.commit()
#add_info_to_tables(2,123,0,0,2)

