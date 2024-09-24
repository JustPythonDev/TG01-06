import sqlite3

conn = sqlite3.connect('bot.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS users (
    id integer primary key autoincrement,
    username text,
    chat_id int
)''')

conn.commit()
conn.close()

