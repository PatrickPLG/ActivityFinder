from flask import Flask, render_template, request, redirect

app = Flask(__name__)
@app.route('/')
def index():
    return render_template("index.html", error=message)

app.run(host='0.0.0.0', port=81, debug=True)