from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "planngo_secret_key"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
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
@app.route('/map')
def map_view():
    places = [
        {"name": "Gateway of India", "lat": 18.9220, "lng": 72.8347},
        {"name": "Marine Drive", "lat": 18.9430, "lng": 72.8238},
    ]
    return render_template("map.html", places=places)

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
# ---------------- Hill-Forts ----------------
@app.route('/hill_forts')
def hill_forts():
    return render_template('hill_forts.html')

@app.route('/raigad')
def raigad():
    return render_template('hill-forts/raigad.html')

@app.route('/lohagad')
def lohagad():
    return render_template('hill-forts/lohagad.html')

@app.route('/rajgad')
def rajgad():
    return render_template('hill-forts/rajgad.html')

@app.route('/pratapgad')
def pratapgad():
    return render_template('hill-forts/pratapgad.html')

@app.route('/harishchandragad')
def harishchandragad():
    return render_template('hill-forts/harishchandragad.html')

@app.route('/sinhagad')
def sinhagad():
    return render_template('hill-forts/sinhagad.html')

@app.route('/visapur')
def visapur():
    return render_template('hill-forts/visapur.html')

@app.route('/torna')
def torna():
    return render_template('hill-forts/torna.html')

@app.route('/daulatabad')
def daulatabad():
    return render_template('hill-forts/daulatabad.html')


# ---------------- Beaches ----------------
@app.route('/Konkan')
def beaches():
    return render_template('Konkan.html')

@app.route('/ganpatipule')
def ganpatipule():
    return render_template('Beach/ganpatipule.html')

@app.route('/alibaug')
def alibaug():
    return render_template('Beach/alibaug.html')

@app.route('/diveagar')
def diveagar():
    return render_template('Beach/diveagar.html')

@app.route('/harihareshwar')
def harihareshwar():
    return render_template('Beach/harihareshwar.html')

@app.route('/kashid')
def kashid():
    return render_template('Beach/kashid.html')

@app.route('/murud')
def murud():
    return render_template('Beach/murud.html')

@app.route('/tarkarli')
def tarkarli():
    return render_template('Beach/tarkarli.html')


# ---------------- Hsitorical places ----------------
@app.route('/ajanta_ellora')
def Historical_places():
    return render_template('ajanta_ellora.html')

@app.route('/ajanta')
def ajanta():
    return render_template('historical_places/ajanta.html')

@app.route('/ellora')
def ellora():
    return render_template('historical_places/ellora.html')

@app.route('/bibi')
def bibi():
    return render_template('historical_places/bibi.html')

@app.route('/girshneshwar')
def girshneshwar():
    return render_template('historical_places/girshneshwar.html')

@app.route('/kailasa')
def kailasa():
    return render_template('historical_places/kailasa.html')


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

# ---------------- OTHER ROUTES (UNCHANGED) ----------------
@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/preplanned')
def preplanned():
    return render_template('preplanned.html')

@app.route('/plan')
def plan():
    return render_template('plan_now.html')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
