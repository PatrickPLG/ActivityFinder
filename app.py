from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'
offers = {}
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
                offers[str(row[0])] = [row[0],row[1],row[2],row[3],row[4], row[5]]
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html")
    return render_template('index.html', offers = offers)


@app.route('/create', methods=['GET', 'POST'])
def create():
    with sqlite3.connect("db.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            if request.method == 'POST':
                begivenhed = request.form.get('begivenhed')
                begivenhed_beskrivelse = request.form.get('begivenhed_beskrivelse')
                lokation = request.form.get('lokation')
                dato = request.form.get('dato')
                tidspunkt = request.form.get('tidspunkt')

                cursor = db.cursor()
                cursor.execute("INSERT INTO offers (creator, activity, date, time, desc) VALUES (?, ?, ?, ?, ?)", (session['username'], begivenhed, dato, tidspunkt, begivenhed_beskrivelse))
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("create.html")
    return render_template("create.html")

@app.route('/get', methods=['GET', 'POST'])
def get_item():
    with sqlite3.connect("db.db") as db:
        try:
            global goods
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

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    with sqlite3.connect("db.db") as db:
        try:
            return render_template("profile.html")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("profile.html")
    return render_template('profile.html')

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

@app.route('/register', methods=['POST', 'GET'])
def register():
    with sqlite3.connect("db.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                name = request.form.get('name')
                adress = request.form.get('adress')
                number = request.form.get('number')

                cursor = db.cursor()
                cursor.execute('select * from users where username = ? and password = ?', (username,password))
                print(cursor.fetchall())
                valid_login = cursor.fetchall()
                
                if valid_login == []:
                    cur = db.cursor()
                    cur.execute("INSERT INTO users(username, password) values (?,?)", (username,password))
                    
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

app.run(host='0.0.0.0', port=81, debug=True)