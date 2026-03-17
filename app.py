from flask import Flask, render_template, request, redirect, session,jsonify
from dotenv import load_dotenv
import uuid
import os
import sqlite3
import requests
import math


app = Flask(__name__)
app.secret_key = "planngo_secret_key"
GOOGLE_API_KEY = "AIzaSyCkIPEHU60BvEC3d598gpel5L9wT0lfai0"

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


@app.route("/api/places/<destination>")
def get_places(destination):

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=tourist+places+in+{destination}&key={GOOGLE_API_KEY}"

    response = requests.get(url)
    data = response.json()

    places = []

    if "results" in data:

        for place in data["results"][:9]:

            places.append({
                "name": place["name"],
                "rating": place.get("rating", "N/A"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            })

    return jsonify({"places": places})

@app.route("/trip")
def trip():
    return render_template("trip.html")

# ---------------- ITINERARY ----------------

@app.route("/itinerary")
def itinerary():

    trip_id = request.args.get("trip_id")
    destination = request.args.get("destination")

    return render_template(
        "itinerary.html",
        trip_id=trip_id,
        destination=destination
    )

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

# ---------------- Save places ----------------
@app.route("/save_places", methods=["POST"])
def save_places():

    data = request.json
    trip_id = data["trip_id"]

    os.makedirs("trips", exist_ok=True)

    file_path = f"trips/{trip_id}.json"

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    return {"status": "success"}

# ---------------- get data ----------------
@app.route("/get_trip/<trip_id>")
def get_trip(trip_id):

    import os
    import json

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TRIPS_FOLDER = os.path.join(BASE_DIR, "trips")

    file_path = os.path.join(TRIPS_FOLDER, f"{trip_id}.json")

    try:
        if not os.path.exists(file_path):
            return {"places": []}

        with open(file_path, "r") as f:
            data = json.load(f)

        return data

    except Exception as e:
        print("ERROR:", e)
        return {"places": []}

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
    
# ---------------- create trip ----------------

@app.route("/create_trip")
def create_trip():

    destination = request.args.get("destination")
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    trip_id = str(uuid.uuid4())

    return redirect(
        f"/map?destination={destination}&lat={lat}&lng={lng}&trip_id={trip_id}"
    )

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
