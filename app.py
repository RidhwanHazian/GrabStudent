from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="GrabStudent"
)

# Predefined valid locations for booking
VALID_LOCATIONS = [
    "UiTM Jasin → Melaka Sentral",
    "UiTM Jasin → Aeon Bandaraya",
    "UiTM Jasin → Muar",
    "UiTM Jasin → MITC"
]

# ----------------- PUBLIC PAGES -----------------

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/location')
def location():
    return render_template('location.html')

# ----------------- AUTHENTICATION -----------------

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("❌ Passwords do not match.")
            return redirect(url_for('signup'))

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            flash("❌ Email already registered.")
            return redirect(url_for('signup'))

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()
        cursor.close()
        flash("✅ Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['name']      # <-- add this
            session['is_admin'] = user.get('is_admin', False)
            flash("✅ Login successful!")
            return redirect(url_for('booking'))
        else:
            flash("❌ Invalid email or password.")
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("✅ Logged out successfully.")
    return redirect(url_for('login'))

# ----------------- BOOKING -----------------

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user_id' not in session:
        flash("⚠️ You must be logged in to book.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        datetime_input = request.form['datetime']

        # Validate locations
        if pickup not in VALID_LOCATIONS or dropoff not in VALID_LOCATIONS:
            flash("❌ Invalid pickup or dropoff location.")
            return redirect(url_for('booking'))

        # Validate future datetime
        booking_time = datetime.fromisoformat(datetime_input)
        if booking_time <= datetime.now():
            flash("❌ Booking date/time must be in the future.")
            return redirect(url_for('booking'))

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO booking (name, pickup, dropoff, datetime, user_id) VALUES (%s, %s, %s, %s, %s)",
            (name, pickup, dropoff, datetime_input, session['user_id'])
        )
        db.commit()
        cursor.close()
        flash("✅ Booking submitted successfully!")

    return render_template('booking.html', locations=VALID_LOCATIONS)

# ----------------- USER PROFILE -----------------

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("⚠️ You must be logged in to view your profile.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM booking WHERE user_id=%s ORDER BY datetime DESC", (session['user_id'],))
    bookings = cursor.fetchall()
    cursor.close()

    return render_template('profile.html', user=user, bookings=bookings)

# ----------------- ADMIN DASHBOARD -----------------

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM booking ORDER BY datetime DESC")
    all_bookings = cursor.fetchall()
    cursor.close()

    return render_template('admin.html', bookings=all_bookings)

# ----------------- RUN SERVER -----------------

if __name__ == '__main__':
    app.run(debug=True)
