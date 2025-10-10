# pip install psycopg2-binary
import psycopg2
from gismeteo_bot import user_data, user_zone

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
    id_tg INTEGER PRIMARY KEY REFERENCES users(id_tg) NOT NULL,
    zone_code INTEGER NOT NULL)
    
    
    """)
    conn.commit()

#create_table_only_one_time()


def add_info_about_user_to_tables(id_tg=user_data.id_tg, name=user_data.user_name, user_name=user_data.username, zone=user_zone.zone, zone_id=user_zone.id_tg):
    print(f"bd's working {id_tg}")
