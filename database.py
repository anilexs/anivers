import sqlite3

def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sondage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        options TEXT NOT NULL,
        emojis TEXT NOT NULL,
        posted INTEGER DEFAULT 0,
        UNIQUE(question)
    )

    ''')

    # Table des questions de quiz
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS question_quiz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        options TEXT NOT NULL,           -- Réponses séparées par %
        correct_index INTEGER NOT NULL   -- Index (0, 1, 2...) de la bonne réponse
    )
    ''')

    # Table des thèmes de quiz
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS theme_quiz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL        -- Nom du thème (ex: "Géographie")
    )
    ''')

    # Table de liaison quiz <-> thème
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS link_quiz_theme (
        quiz_id INTEGER NOT NULL,
        theme_id INTEGER NOT NULL,
        PRIMARY KEY (quiz_id, theme_id),
        FOREIGN KEY (quiz_id) REFERENCES question_quiz(id) ON DELETE CASCADE,
        FOREIGN KEY (theme_id) REFERENCES theme_quiz(id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

def ajouter_sondage(question, options_list, emojis_list):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    options = '%'.join(options_list)
    emojis = '%'.join(emojis_list)

    cursor.execute('''
    INSERT INTO sondage (question, options, emojis, posted)
    VALUES (?, ?, ?, 0)
    ''', (question, options, emojis))
    conn.commit()
    conn.close()
    print("Sondage ajouté !")

def get_sondage(sondage_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    cursor.execute("SELECT question, options, emojis, posted FROM sondage WHERE id = ?", (sondage_id,))
    data = cursor.fetchone()
    conn.close()
    if not data:
        return None
    question, options_str, emojis_str, posted = data
    options = options_str.split('%')
    emojis = emojis_str.split('%')
    return {
        "question": question,
        "options": options,
        "emojis": emojis,
        "posted": bool(posted)
    }
