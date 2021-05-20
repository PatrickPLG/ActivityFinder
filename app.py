from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'
@app.route('/', methods=['POST', 'GET'])
def index():
    if session.get('username') == None:
        return render_template("login.html")
    return render_template("index.html")


@app.route('/create', methods=['GET', 'POST'])
def create():
    with sqlite3.connect("db.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            if request.method == 'POST':
                beskrivelse = request.form.get('beskrivelse')
                udløbsdato = request.form.get('udløbsdato')
                lokation = request.form.get('lokation')

                file = request.files["file"]
                file.save(os.path.join("static/images", file.filename))

                cursor = db.cursor()
                cursor.execute("INSERT INTO Varer (beskrivelse, udløbsdato, lokation, datastore, seller) VALUES (?, ?, ?, ?, ?)", (beskrivelse, udløbsdato, lokation, file.filename, session['username']))
                cursor.execute("UPDATE Person_information SET points = points + 10 WHERE username = '" + session['username'] + "'")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("create.html")
    return render_template("create.html")



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