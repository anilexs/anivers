import sqlite3

theme = [
    {'themes': "convention"},
    {'themes': "anime"},
    {'themes': "manga"},
    {'themes': "manga2"},
    {'themes': "manga23"},
    {'themes': "manga234"},
    {'themes': "manga2345"},
    {'themes': "manga23456"},
    {'themes': "manga234567"},
    {'themes': "manga2345678"},
    {'themes': "manga23456789"},
    {'themes': "manga234567890"},
    {'themes': "manga2345678901"},
    {'themes': "manga23456789012"},
    {'themes': "manga234567890123"},
    {'themes': "manga2345678901234"},
    {'themes': "manga23456789012345"},
]

def insert_theme_quiz():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Récupère tous les thèmes déjà présents dans la BDD
    cursor.execute("SELECT name FROM theme_quiz")
    existing_themes = {row[0] for row in cursor.fetchall()}  # Set pour accès rapide

    # Parcourt les nouveaux thèmes
    for s in theme:
        theme_name = s['themes']
        if theme_name not in existing_themes:
            cursor.execute(
                "INSERT INTO theme_quiz (name) VALUES (?)",
                (theme_name,)
            )
            print(f"Thème ajouté : {theme_name}")
        else:
            print(f"Thème déjà présent : {theme_name}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    insert_theme_quiz()
