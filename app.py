from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'
offers = {}
socketio = SocketIO(app, cors_allowed_origins='*')
@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("db.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM offers")
            all_items = cursor.fetchall()

            for row in all_items:
                offers[str(row[0])] = [row[0],row[1],row[2],row[3],row[4], row[5], row[6], row[7]]
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html")
    return render_template('index.html', offers = offers)

# Siden hvor man opretter en aktivitet
@app.route('/create', methods=['GET', 'POST'])
def create():
    # Opretter forbindelse til databasen
    with sqlite3.connect("db.db") as db:
        try:
            # Hvis man ikke er logget ind sendes man til login siden
            if session.get('username') == None:
                return render_template("login.html")
            # Hvis der bliver trykket på knappen på siden
            if request.method == 'POST':
                # Får data fra alle inputfelterne
                begivenhed = request.form.get('begivenhed')
                begivenhed_beskrivelse = request.form.get('begivenhed_beskrivelse')
                lokation = request.form.get('lokation')
                dato = request.form.get('dato')
                tidspunkt = request.form.get('tidspunkt')
                # Først hentes profilbilledet og derefter indsættes alt data ind i databasen
                cursor = db.cursor()
                cursor.execute("SELECT profile_picture FROM person_information WHERE username = '" + session['username'] + "'")
                profile_picture = cursor.fetchall()
                cursor.execute("INSERT INTO offers (creator, activity, date, time, desc, location, image) VALUES (?, ?, ?, ?, ?, ?,?)", (session['username'], begivenhed, dato, tidspunkt, begivenhed_beskrivelse, lokation, profile_picture[0][0]))
        # Hvis der er en fejl med databasen
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("create.html")
    return render_template("create.html")

@app.route('/get', methods=['GET', 'POST'])
def get_item():
    with sqlite3.connect("db.db") as db:
        try:
            if request.method == 'POST':
                val = request.get_json().get('val')
                print(val)
                cursor = db.cursor()
                cursor.execute("SELECT * FROM offers_joined WHERE id = ? AND username = ?", (val, session['username']))
                offer_check = cursor.fetchall()
                if offer_check == []:
                    cursor.execute("INSERT INTO offers_joined VALUES (?,?)", (session['username'], val))
                else:
                    print("Er i DB")
            return redirect("/")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("/")
    return redirect("/")

@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    with sqlite3.connect("db.db") as db:
        try:
            if request.method == 'POST':
                unsubscribe_offer = request.get_json().get('val')
                print(unsubscribe_offer)
                cursor = db.cursor()
                cursor.execute("DELETE FROM offers_joined WHERE id = ? AND username = ?", (unsubscribe_offer, session['username']))
            return redirect("joined")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("joined")
    return redirect("joined")

def log_the_user_in(username):
    return redirect("/")

@app.route('/joined', methods=['GET', 'POST'])
def joined():
    with sqlite3.connect("db.db") as db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM offers INNER JOIN offers_joined ON offers.id = offers_joined.id WHERE offers_joined.username = '" + session['username'] + "'")
            user_joined = cursor.fetchall()
            return render_template("joined.html", user_joined=user_joined)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("joined.html")
    return render_template("joined.html", user_joined=user_joined)

def log_the_user_in(username):
    return redirect("/")

@app.route('/login', methods=['POST', 'GET'])
def login():
    with sqlite3.connect("db.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                cursor = db.cursor()
                cursor.execute('select * from users where username = ? and password = ?', (username,password))
                valid_login = cursor.fetchall()

                if valid_login != []:
                    session['username'] = request.form['username']
                    
                    return log_the_user_in(request.form['username'])
                else:
                    error = 'Invalid username/password'
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("login.html", error=message)

    return render_template('login.html', error=error)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    with sqlite3.connect('db.db') as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cur = db.cursor()
            cur.execute("select * from person_information where username = '" + session['username'] + "'")
            personalInformation = cur.fetchall()
            print(personalInformation)

            if request.method == 'POST':
                name = request.form.get('navn')
                file = request.files["file"]
                file.save(os.path.join("static/images", file.filename))
                cur.execute("UPDATE offers SET image = ? WHERE creator = ?", (file.filename, session['username']))
                cur.execute("UPDATE person_information SET name = ?, profile_picture = ? WHERE username = ?", (name, file.filename, session['username']))
                return redirect("/profile")

            return render_template("profile.html", personalInformation=personalInformation)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("profile.html")
    return render_template("profile.html", personalInformation=personalInformation)

@app.route('/register', methods=['POST', 'GET'])
def register():
    with sqlite3.connect("db.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                name = request.form.get('name')

                cursor = db.cursor()
                cursor.execute('select * from users where username = ? and password = ?', (username,password))
                print(cursor.fetchall())
                valid_login = cursor.fetchall()
                
                if valid_login == []:
                    cur = db.cursor()
                    cur.execute("INSERT INTO users(username, password) values (?,?)", (username,password))
                    cur.execute("INSERT INTO person_information(username, name, profile_picture) values (?,?,?)", (username,name,'profilepicture.png'))
                    
                    render_template('login.html', error=error)
                else:
                    error = 'Kontoen eksiterer allerede'
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("register.html", error=message)
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', default=None)
    return render_template('login.html')

@app.route('/chat')
def chat():
    with sqlite3.connect("db.db") as db:
        try:
            cur = db.cursor()
            cur.execute("SELECT name FROM person_information WHERE username = '" + session['username'] + "'")
            username = cur.fetchall()
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("register.html", error=message)
    return render_template('chat.html', username=username)

@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)

if __name__ == '__main__':
	socketio.run(app)