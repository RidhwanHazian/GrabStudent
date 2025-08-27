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

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'iwghostpride@gmail.com'   # sender email
app.config['MAIL_PASSWORD'] = 'edbucokhnzajivxy'  # App Password if Gmail
app.config['MAIL_DEFAULT_SENDER'] = ('Grab Student', 'iwghostpride@gmail.com')

mail = Mail(app)


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
        user_type = request.form['user_type']  # either 'customer' or 'driver'

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))

        cursor = db.cursor(dictionary=True)

        # Check duplicate email in users or drivers
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.execute("SELECT * FROM drivers WHERE email = %s", (email,))
        existing_driver = cursor.fetchone()

        if existing_user or existing_driver:
            flash("Email already registered. Please log in.")
            cursor.close()
            return redirect(url_for('signup'))

        # Insert based on role
        if user_type == "driver":
            cursor.execute(
                "INSERT INTO drivers (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
        else:  # customer
            cursor.execute(
                "INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)",
                (name, email, password, "customer")
            )

        db.commit()
        cursor.close()

        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)

        # First check in users table
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_type'] = user['user_type']
            session['is_admin'] = (user['user_type'] == 'admin')

            flash("✅ Login successful!")

            # Redirect based on role
            if user['user_type'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:  # customer
                return redirect(url_for('profile'))

        # If not found in users, check in drivers table
        cursor.execute("SELECT * FROM drivers WHERE email = %s AND password = %s", (email, password))
        driver = cursor.fetchone()
        cursor.close()

        if driver:
            session['user_id'] = driver['driver_id']
            session['user_name'] = driver['name']
            session['user_type'] = 'driver'
            session['is_admin'] = False

            flash("✅ Login successful!")
            return redirect(url_for('driver_dashboard'))

        flash("❌ Invalid email or password.")

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

        # ✅ No more VALID_LOCATIONS check, just make sure fields are not empty
        if not pickup or not dropoff:
            flash("❌ Pickup and dropoff locations cannot be empty.")
            return redirect(url_for('booking'))

        # Validate future datetime
        try:
            booking_time = datetime.fromisoformat(datetime_input)
        except ValueError:
            flash("❌ Invalid date/time format.")
            return redirect(url_for('booking'))

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

    return render_template('booking.html')


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

# ----------------- DRIVER DASHBOARD -----------------
@app.route('/driver')
def driver_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'driver':
        flash("⚠️ Driver access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM booking WHERE driver_id IS NULL ORDER BY datetime ASC")
    bookings = cursor.fetchall()
    cursor.close()

    return render_template('driver.html', bookings=bookings)


# ----------------- SELECT BOOKING ROUTE -----------------
@app.route('/take_booking/<int:booking_id>', methods=['POST'])
def take_booking(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'driver':
        flash("⚠️ Driver access required.")
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "UPDATE booking SET driver_id = %s, status = %s WHERE id = %s", 
        (session['user_id'], 'Pending', booking_id)   # ✅ Capital P
    )
    db.commit()
    cursor.close()

    flash("✅ You have taken this booking!")
    return redirect(url_for('driver_dashboard'))


# ----------------- SELECTED BOOKING PAGE -----------------
@app.route('/driver/bookings')
def driver_bookings():
    if 'user_id' not in session or session.get('user_type') != 'driver':
        flash("⚠️ Driver access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM booking WHERE driver_id = %s ORDER BY datetime ASC",
        (session['user_id'],)
    )
    bookings = cursor.fetchall()
    cursor.close()

    return render_template('driver_bookings.html', selected=bookings)


# ----------------- UPDATE BOOKING STATUS -----------------
@app.route('/driver/update_status/<int:booking_id>', methods=['POST'])
def update_booking_status(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'driver':
        flash("⚠️ Driver access required.")
        return redirect(url_for('login'))

    new_status = request.form.get('status')

    # Validate status
    if new_status not in ['Pending', 'Accepted', 'On the way', 'Completed', 'Cancelled']:
        flash("❌ Invalid status.")
        return redirect(url_for('driver_bookings'))

    cursor = db.cursor(dictionary=True)
    # Update booking status
    cursor.execute(
        "UPDATE booking SET status = %s WHERE id = %s AND driver_id = %s",
        (new_status, booking_id, session['user_id'])
    )
    db.commit()

    # Get customer info
    cursor.execute(
        "SELECT name, email FROM users WHERE id = (SELECT user_id FROM booking WHERE id=%s)",
        (booking_id,)
    )
    customer = cursor.fetchone()
    cursor.close()

    # Send email notification
    if customer:
        try:
            msg = Message(
                subject=f"Your Booking Status Updated: {new_status}",
                recipients=[customer['email']],
                body=f"Hi {customer['name']},\n\nYour booking status has been updated to: {new_status}.\n\nThank you for using Grab Student."
            )

            msg.html = f"""
            <p>Hi {customer['name']},</p>
            <p>Your booking status has been updated to: 
            <b style="color: {'green' if new_status=='Completed' else 'red' if new_status=='Cancelled' else 'blue'};">
            {new_status}</b>
            </p>
            <p>Thank you for using Grab Student.</p>
            """

            mail.send(msg)
        except Exception as e:
            print("Error sending email:", e)

    flash(f"✅ Booking status updated to {new_status}.")
    return redirect(url_for('driver_bookings'))  # ✅ Add this return



# ----------------- ADMIN DASHBOARD -----------------

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)

    # Total bookings
    cursor.execute("SELECT COUNT(*) as total FROM booking")
    total_bookings = cursor.fetchone()['total']

    # Completed bookings
    cursor.execute("SELECT COUNT(*) as completed FROM booking WHERE status='Completed'")
    completed_bookings = cursor.fetchone()['completed']

    # Pending bookings
    cursor.execute("SELECT COUNT(*) as pending FROM booking WHERE status='Pending'")
    pending_bookings = cursor.fetchone()['pending']

    # Cancelled bookings
    cursor.execute("SELECT COUNT(*) as cancelled FROM booking WHERE status='Cancelled'")
    cancelled_bookings = cursor.fetchone()['cancelled']

    # Recent bookings (last 5)
    cursor.execute("""
        SELECT b.id, b.name, b.pickup, b.dropoff, b.datetime, b.status, d.name as driver_name
        FROM booking b
        LEFT JOIN drivers d ON b.driver_id = d.driver_id
        ORDER BY b.datetime DESC
        LIMIT 5
    """)
    recent_bookings = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin.html',
        total_bookings=total_bookings,
        completed_bookings=completed_bookings,
        pending_bookings=pending_bookings,
        cancelled_bookings=cancelled_bookings,
        recent_bookings=recent_bookings
    )


# ----------------- RUN SERVER -----------------

if __name__ == '__main__':
    app.run(debug=True)
