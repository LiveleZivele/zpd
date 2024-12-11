import sqlite3
import os

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'virtualabiblioteka.db')
    conn = sqlite3.connect('virtualabiblioteka.db')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
       CREATE TABLE IF NOT EXISTS lietotajs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vards TEXT NOT NULL,
            uzvards TEXT NOT NULL,
            epasts TEXT NOT NULL,
            talr_num TEXT NOT NULL,
            parole TEXT NOT NULL
            )''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gramata(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nosaukums TEXT NOT NULL,
            autors TEXT NOT NULL,
            pieejams BOOLEAN NOT NULL DEFAULT 1       
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS izlasitas_gramatas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pabeigts_lasit_datums TEXT NOT NULL,
            id_lietotajs INTEGER NOT NULL,
            id_gramata INTEGER NOT NULL,
            FOREIGN KEY (id_gramata) REFERENCES gramata(id),
            FOREIGN KEY (id_lietotajs) REFERENCES lietotajs(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS velas_lasit_gramatas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ielikts_saraksta TEXT NOT NULL,
            id_lietotajs INTEGER NOT NULL,
            id_gramata INTEGER NOT NULL,
            FOREIGN KEY (id_gramata) REFERENCES gramata(id),
            FOREIGN KEY (id_lietotajs) REFERENCES lietotajs(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gr_noma(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_datums TEXT NOT NULL,
            lidz_datums TEXT NOT NULL,
            is_returned INTEGER DEFAULT 0,
            id_lietotajs INTEGER NOT NULL,
            id_gramata INTEGER NOT NULL,
            FOREIGN KEY (id_lietotajs) REFERENCES lietotajs(id),
            FOREIGN KEY (id_gramata) REFERENCES gramata(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saturs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_gr_noma INTEGER NOT NULL,
            FOREIGN KEY (id_gr_noma) REFERENCES gr_noma(id)
        )
    ''')
    conn.commit()
    conn.close()

def gramatas_kuras_dotas():
    dati_gramatas = [('Sešas vielas, kas maina tavu dzīvi','Dāvids Jp Filipss'),
              ('Piktais Sentiments', 'Silvija Brice' ),
              ('Bērnudienas Komunālijā', 'Zane Daudziņa' ),
              ('Kaķa Semanuela Piedzīvojumi', 'Liene Behmane' ),
              ('Mazais Pūķis Kokosrieksts Pēta Seno Ēģipti', 'Ingo Zīgners' ),
              ('Brīvībene', 'Svens Kuzmins' ),
              ('Pēc Otrā Zvana', 'Ēriks Vilsons' ),
              ('Caciki Un Muterīte', 'Moni Nilsone' ),
              ('Marta Ir Aizmigusi', 'Romija Hausmane' ),
              ('Kleita Ar Gundegu Rakstu', 'Epu Nuotio' ),
              ('Atnāciet Rīt!', 'Dace Judina' ),
              ('Pāru Lielais (iz)aicinājums', 'Gatis Līdums' )
             
              ]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO gramata (nosaukums, autors) VALUES (?, ?)', dati_gramatas)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    gramatas_kuras_dotas()
    