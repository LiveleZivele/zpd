from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import get_db_connection, init_db
from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
bcrypt = Bcrypt(app)
db = get_db_connection()
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

   
    cursor.execute('SELECT id, nosaukums, autors, pieejams FROM gramata LIMIT 6')
    first_6_books = cursor.fetchall()

    
    cursor.execute('SELECT id, nosaukums, autors, pieejams FROM gramata ORDER BY id DESC LIMIT 6')
    last_6_books = cursor.fetchall()

    user_id = session.get('user_id')
    liked_books = []
    
    if user_id:
        cursor.execute('SELECT id_gramata FROM velas_lasit_gramatas WHERE id_lietotajs = ?', (user_id,))
        liked_books = [row[0] for row in cursor.fetchall()]

    conn.close()

   
    return render_template('index.html', 
                           first_6_books=first_6_books, 
                           last_6_books=last_6_books, 
                           liked_books=liked_books)



@app.route('/take_book', methods=['POST'])
@login_required
def take_book():
    book_id = request.json.get('book_id') 
    if not book_id:
        return jsonify({'error': 'No book ID provided'}), 400
    return handle_take_book(book_id)

def handle_take_book(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

  
    cursor.execute('SELECT pieejams FROM gramata WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    if not book or book[0] == 0:
        return jsonify({'error': 'Grāmata nav pieejama'}), 400

   
    current_date = datetime.now()
    return_date = current_date + timedelta(days=30)
    cursor.execute(
        '''
        INSERT INTO gr_noma (id_lietotajs, id_gramata, no_datums, lidz_datums)
        VALUES (?, ?, ?, ?)
        ''',
        (user_id, book_id, current_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'))
    )

    
    cursor.execute('UPDATE gramata SET pieejams = 0 WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': 'Grāmata tika paņemta veiksmīgi'})




@app.route('/take_book/<int:book_id>', methods=['POST'])
def take_specific_book(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('SELECT pieejams FROM gramata WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    if not book or book[0] == 0:
        conn.close()
        return 'Grāmata nav pieejama', 400

   
    cursor.execute('UPDATE gramata SET pieejams = 0 WHERE id = ?', (book_id,))

   
    from datetime import datetime, timedelta
    no_datums = datetime.now().strftime('%Y-%m-%d')
    lidz_datums = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    cursor.execute(
        'INSERT INTO gr_noma (no_datums, lidz_datums, id_lietotajs) VALUES (?, ?, ?)',
        (no_datums, lidz_datums, user_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('manasgramatas'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
     if request.method == 'POST':
        epasts = request.form.get('epasts')  
        parole = request.form.get('parole')  

        if not epasts or not parole:
            return "Lūdzu aizpildat ailes", 400  

        conn = get_db_connection()
        cursor = conn.cursor()

        
        cursor.execute('SELECT id, parole FROM lietotajs WHERE epasts = ?', (epasts,))
        user = cursor.fetchone()
        conn.close()

        if user:
            
            if bcrypt.check_password_hash(user[1], parole):
                session['user_id'] = user[0]  
                return redirect(url_for('profils'))  
            else:
                return "Nepareizi, lūdzu ievadat atkal", 401  
        else:
            return "Nepareizi, lūdzu ievadat atkal", 401 

     return render_template('login.html')

@app.route('/return_book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()


    cursor.execute(''' 
        UPDATE gr_noma
        SET is_returned = 1
        WHERE id_lietotajs = ? AND id_gramata = ? AND is_returned = 0
    ''', (user_id, book_id))

   
    cursor.execute(''' 
        UPDATE gramata
        SET pieejams = 1
        WHERE id = ? 
    ''', (book_id,))

    conn.commit()
    conn.close()

 
    return redirect(url_for('izlasitasgramatas'))

@app.route('/register' , methods=['GET', 'POST'])
def register():
   if request.method == 'POST':
        vards = request.form['vards']
        uzvards = request.form['uzvards']
        epasts = request.form['epasts']
        talr_num = request.form['talr_num']
        parole = request.form['parole']

        hashed_password = bcrypt.generate_password_hash(parole).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

       
        cursor.execute('''
            INSERT INTO lietotajs (vards, uzvards, epasts, talr_num, parole)
            VALUES (?, ?, ?, ?, ?)
        ''', (vards, uzvards, epasts, talr_num, hashed_password))

      
        user_id = cursor.lastrowid  

        conn.commit()
        conn.close()

        
        session['user_id'] = user_id

       
        return redirect(url_for('profils'))

   return render_template('register.html')

@app.route('/manasgramatas', methods=['GET', 'POST'])
@login_required
def manasgramatas():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

   
    cursor.execute('''
        SELECT g.nosaukums, g.autors, n.no_datums, n.lidz_datums, g.id
        FROM gr_noma n
        JOIN gramata g ON n.id_gramata = g.id
        WHERE n.id_lietotajs = ? AND n.is_returned = 0
    ''', (user_id,))
    taken_books = cursor.fetchall()
    conn.close()

    return render_template('manasgramatas.html', taken_books=taken_books)
    


@app.route('/profils',methods=['GET' , 'POST'])
@login_required
def profils():
    if request.method == 'POST':  
        session.pop('user_id', None) 
        return redirect(url_for('login'))  
    

    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login')) 
    

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT vards, uzvards FROM lietotajs WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('profils.html', user=user)
    else:
        return render_template('login.html') 
    
@app.route('/veloslasit', methods=['GET', 'POST'])
def wishlist():
    user_id = session.get('user_id')
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()

      
        cursor.execute('''SELECT g.id, g.nosaukums, g.autors, v.ielikts_saraksta 
                         FROM velas_lasit_gramatas v
                         JOIN gramata g ON v.id_gramata = g.id
                         WHERE v.id_lietotajs = ?''', (user_id,))
        wishlist_books = cursor.fetchall()

        if request.method == 'POST':
           
            book_id = request.form.get('remove_books')
            if book_id:
                
                cursor.execute('''DELETE FROM velas_lasit_gramatas 
                                  WHERE id_gramata = ? AND id_lietotajs = ?''', 
                               (book_id, user_id))
                conn.commit()

            
            return redirect(url_for('wishlist'))

        conn.close()
        return render_template('veloslasit.html', wishlist_books=wishlist_books)
    return redirect(url_for('login'))

@app.route('/izlasitasgramatas', methods=['GET'])
@login_required
def izlasitasgramatas():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('''
        SELECT g.nosaukums, g.autors, n.no_datums
        FROM gr_noma n
        JOIN gramata g ON n.id_gramata = g.id
        WHERE n.id_lietotajs = ? AND n.is_returned = 1
    ''', (user_id,))

    returned_books = cursor.fetchall()
    conn.close()

    return render_template('izlasitasgramatas.html', returned_books=returned_books)

@app.route('/iest', methods=['GET', 'POST'])
@login_required
def iest():
    user_id = session.get('user_id')
    message = None 

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_password':
           
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')

            if not current_password or not new_password:
                message = "Visas ailes ir jāaizpilda (Password)"
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT parole FROM lietotajs WHERE id = ?', (user_id,))
                user = cursor.fetchone()

                if user and bcrypt.check_password_hash(user[0], current_password):
                    hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                    cursor.execute('UPDATE lietotajs SET parole = ? WHERE id = ?', (hashed_new_password, user_id))
                    conn.commit()
                    conn.close()
                    message = "Parole veiksmīgi nomainīta"
                else:
                    conn.close()
                    message = "Nepareiza pašreizējā parole"

        elif action == 'change_email':
           
            current_email = request.form.get('current_email')
            new_email = request.form.get('new_email')

            if not current_email or not new_email:
                message = "Visas ailes ir jāaizpilda (Email)"
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT epasts FROM lietotajs WHERE id = ?', (user_id,))
                user = cursor.fetchone()

                if user and user[0] == current_email:
                    cursor.execute('UPDATE lietotajs SET epasts = ? WHERE id = ?', (new_email, user_id))
                    conn.commit()
                    conn.close()
                    message = "Epasts veiksmīgi nomainīts"
                else:
                    conn.close()
                    message = "Nepareizs pašreizējais epasts"

    return render_template('iestatijumi.html', message=message)



@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    user_id = session.get('user_id')
    book_id = request.form.get('book_id')  

    if not user_id or not book_id:  
        return "Ludzu pieslēdzaties sistēmā", 500  

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

       
        cursor.execute('''
            SELECT * FROM velas_lasit_gramatas 
            WHERE id_lietotajs = ? AND id_gramata = ?
        ''', (user_id, book_id))
        existing_entry = cursor.fetchone()

        if existing_entry:
            conn.close()
            return "Book already in wishlist", 400 

       
        cursor.execute('''
            INSERT INTO velas_lasit_gramatas (id_lietotajs, id_gramata)
            VALUES (?, ?)
        ''', (user_id, book_id))
        conn.commit()
        conn.close()
        return redirect(url_for('wishlist'))  
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred", 500


if __name__ == '__main__':
 init_db()
 app.run(debug=True)




    
