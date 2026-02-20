from flask import Flask, render_template, request, redirect, session,jsonify
from dotenv import load_dotenv
import os
import sqlite3
import requests
import math


app = Flask(__name__)
app.secret_key = "planngo_secret_key"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)


# ---------------- HOME ----------------
@app.route('/')
def home():
    user = None
    if 'user_id' in session:
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE id=?",
            (session['user_id'],)
        ).fetchone()

    return render_template('welcome.html', user=user)

# ---------------- MAP ----------------
@app.route("/map")
def map_page():
    print(request.args)
    return render_template("map.html")
    

# ---------------- TRIP ----------------
@app.route("/trip")
def trip():
    return render_template("trip.html")

# ---------------- ITINERARY ----------------

@app.route("/itinerary")
def itinerary():
    return render_template("itinerary_result.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        if user:
            session['user_id'] = user['id']
            session['user'] = user['name']
            return redirect('/')
        else:
            return "Invalid email or password"

    return render_template('login.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            return "Passwords do not match"

        try:
            db = get_db()
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            db.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Email already exists"

    return render_template('signup.html')

# ---------------- CHECK LOGIN FOR PLAN TRIP ----------------
@app.route('/check_login_trip')
def check_login_trip():
    if session.get('user'):
        return redirect('/trip')
    else:
        return redirect('/login')

# ---------------- AI FORT SEARCH ----------------
@app.route("/fort")
def fort_page():
    return render_template("fort.html")

@app.route("/find_fort", methods=["POST"])
def find_fort():
    fort_name = request.form["fort_name"]

    user_lat = 18.5204
    user_lon = 73.8567

    url = f"https://nominatim.openstreetmap.org/search?q={fort_name}&format=json"
    res = requests.get(url, headers={"User-Agent":"plango"})
    data = res.json()

    if len(data) == 0:
        return render_template("fort.html",
            result={"name":fort_name,"location":"Not Found","distance":"N/A"})

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    location = data[0]["display_name"]

    distance = calculate_distance(user_lat,user_lon,lat,lon)

    return render_template("fort.html",
        result={
            "name":fort_name,
            "location":location,
            "distance":distance
        })

# ---------------- PROFILE ----------------
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id=?",
        (session['user_id'],)
    ).fetchone()

    return render_template('profile.html', user=user)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- OTHER ROUTES ----------------
@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/preplanned')
def preplanned():
    return render_template('preplanned.html')


# ---------------- Hill-Forts ----------------
@app.route("/hill_forts")
def hill_forts():
    return render_template("hill_forts.html")

# ---------------- Beaches ----------------
@app.route('/Beaches')
def beaches():
    return render_template('Beaches.html')

# ---------------- Wildlife ----------------
@app.route('/Wildlife')
def wildlife():
    return render_template('Wildlife.html')

# ---------------- Seasonal ----------------
@app.route('/Summer')
def summer():
    return render_template('Summer.html')

@app.route('/Monsoon')
def Monsoon():
    return render_template('Monsoon.html')

@app.route('/Winter')
def Winter():
    return render_template('Winter.html')

@app.route('/spring')
def spring():
    return render_template('spring.html')

@app.route('/autumn')
def autumn():
    return render_template('autumn.html')

@app.route('/explore_')
def explore_():
    return render_template('explore_.html')
# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
