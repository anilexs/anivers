import sqlite3

sondages = [
    {
        'question': "Quel est ton genre d’anime préféré ?",
        'options': "Shonen;Shojo;Seinen;Isekai;Slice of Life",
        'emojis': "🥊;💖;🧠;🌌;🍰"
    },
    {
        'question': "Tu préfères lire des mangas en papier ou en numérique ?",
        'options': "Papier;Numérique;Les deux;Aucun",
        'emojis': "📚;📱;🤷‍♂️;🚫"
    },
    {
        'question': "Quel est ton studio d’animation favori ?",
        'options': "Ghibli;MAPPA;Ufotable;Toei;Bones",
        'emojis': "🏯;🗺️;🗡️;🐉;💀"
    },
    {
        'question': "Tu vas en convention pour…",
        'options': "Les cosplays;Les stands;Les invités;Les amis;Les goodies",
        'emojis': "👗;🛍️;🎤;🧑‍🤝‍🧑;🎁"
    },
    {
        'question': "Quel est le meilleur opening d’anime selon toi ?",
        'options': "Attack on Titan;Naruto;One Piece;Demon Slayer;Autre",
        'emojis': "🗻;🍥;☠️;🗡️;❓"
    },
    {
        'question': "Tu préfères les animés doublés ou en VOSTFR ?",
        'options': "VOSTFR;VF;Les deux;Aucun",
        'emojis': "🇯🇵;🇫🇷;🤷;🚫"
    },
    {
        'question': "Quel est ton personnage féminin préféré ?",
        'options': "Mikasa;Hinata;Asuna;Rem;Autre",
        'emojis': "⚔️;🏐;🗡️;💙;❓"
    },
    {
        'question': "Tu collectionnes…",
        'options': "Figurines;Mangas;Posters;Peluches;Rien",
        'emojis': "🗿;📖;🖼️;🧸;🚫"
    },
    {
        'question': "Quel est ton anime de sport favori ?",
        'options': "Haikyuu!!;Kuroko no Basket;Free!;Yowamushi Pedal;Autre",
        'emojis': "🏐;🏀;🏊;🚴;❓"
    },
    {
        'question': "Tu préfères aller en convention…",
        'options': "Seul;Avec des amis;En famille;Avec un cosplay;Jamais",
        'emojis': "🧍;🧑‍🤝‍🧑;👨‍👩‍👧‍👦;👘;🚫"
    },
]

def insert_sondages():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    for s in sondages:
        options_db = s['options'].replace(';', '%')
        emojis_db = s['emojis'].replace(';', '%')
        cursor.execute(
            "INSERT INTO sondage (question, options, emojis, posted) VALUES (?, ?, ?, 0)",
            (s['question'], options_db, emojis_db)
        )
    conn.commit()
    conn.close()
    print("10 sondages anime/manga/convention ajoutés !")

if __name__ == "__main__":
    insert_sondages()