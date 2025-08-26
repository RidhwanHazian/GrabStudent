from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="GrabStudent"
)

# --------------------------
# Home & Pages
# --------------------------
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

# --------------------------
# Signup
# --------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("❌ Passwords do not match.")
            return redirect(url_for('signup'))

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            flash("❌ Email already registered.")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        db.commit()
        cursor.close()
        flash("✅ Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('signup.html')

# --------------------------
# Login
# --------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash("✅ Login successful!")
            return redirect(url_for('booking'))
        else:
            flash("❌ Invalid email or password.")
            return redirect(url_for('login'))

    return render_template('login.html')

# --------------------------
# Logout
# --------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("✅ Logged out successfully.")
    return redirect(url_for('login'))

# --------------------------
# Booking
# --------------------------
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user_id' not in session:
        flash("⚠️ You must be logged in to book.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        pickup = request.form['pickup'].strip()
        dropoff = request.form['dropoff'].strip()
        datetime = request.form['datetime']

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO booking (name, pickup, dropoff, datetime, user_id) VALUES (%s, %s, %s, %s, %s)",
            (name, pickup, dropoff, datetime, session['user_id'])
        )
        db.commit()
        cursor.close()
        flash("✅ Booking submitted successfully!")

    return render_template('booking.html')

# --------------------------
# Run app
# --------------------------
if __name__ == '__main__':
    app.run(debug=True)
