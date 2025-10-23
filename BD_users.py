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
        id_tg BIGINT NOT NULL UNIQUE,
        name VARCHAR(150),
        user_name VARCHAR(100))
    """)
    # CREATE TABLE time_zone
    cursor.execute("""
    CREATE TABLE time_zone(
    id_tg BIGINT PRIMARY KEY REFERENCES users(id_tg) NOT NULL,
    zone_code INTEGER NOT NULL)
    
    
    """)
    conn.commit()
#create_table_only_one_time()

def show():
    cursor.execute("""
    SELECT time_zone.* from time_zone join users on users.id_tg = time_zone.id_tg where users.name = %s;
        """, ('Vincent',))
    res = cursor.fetchall()
    return res

#print(show())

def test():
    cursor.execute("""
    DELETE FROM users WHERE id=%s;
    """, (1,))
    conn.commit()
    #res = cursor.fetchall()
    #return res
#test()