import sqlite3

theme = [
    {
        'themes': "anime",
    },
    {
        'themes': "manga",
    },
]

def insert_theme_quiz():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    for s in theme:
        cursor.execute(
            "INSERT INTO theme_quiz (name) VALUES (?)",
            (s['question'], options_db, emojis_db)
        )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    insert_sondages()