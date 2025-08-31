from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime
from threading import Thread

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

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


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
            elif user['user_type'] == 'driver':
                return redirect(url_for('driver_dashboard'))
            else:  # customer
                return redirect(url_for('customer_dashboard'))


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
@app.route('/logout', methods=['GET','POST'])
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

    status_filter = request.args.get('status')  # get ?status=

    cursor = db.cursor(dictionary=True)
    if status_filter:
        cursor.execute(
            "SELECT * FROM booking WHERE driver_id=%s AND status=%s ORDER BY datetime ASC",
            (session['user_id'], status_filter)
        )
    else:
        cursor.execute(
            "SELECT * FROM booking WHERE driver_id=%s ORDER BY datetime ASC",
            (session['user_id'],)
        )

    bookings = cursor.fetchall() or []  # ensure it's a list
    cursor.close()

    return render_template(
        'driver_bookings.html',
        selected=bookings,
        status_filter=status_filter
    )


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

    # Fetch booking + customer + driver name (LEFT JOIN in case driver unassigned)
    cursor.execute("""
        SELECT u.name AS customer_name, u.email AS customer_email,
               b.pickup, b.dropoff, b.datetime,
               d.name AS driver_name, b.driver_id
        FROM booking b
        JOIN users u ON u.id = b.user_id
        LEFT JOIN drivers d ON d.driver_id = b.driver_id
        WHERE b.id = %s
    """, (booking_id,))
    details = cursor.fetchone()

    if not details:
        cursor.close()
        flash("❌ Booking not found.")
        return redirect(url_for('driver_bookings'))

    driver_display = details['driver_name'] if details['driver_name'] else "Currently unassigned"

    # Perform the update
    if new_status == 'Cancelled':
        cursor.execute(
            "UPDATE booking SET status = 'Pending', driver_id = NULL WHERE id = %s AND driver_id = %s",
            (booking_id, session['user_id'])
        )
    else:
        cursor.execute(
            "UPDATE booking SET status = %s WHERE id = %s AND driver_id = %s",
            (new_status, booking_id, session['user_id'])
        )
    db.commit()
    cursor.close()

    # Send email notification
    try:
        msg = Message(
            subject=f"Your Booking Status Updated: {new_status}",
            recipients=[details['customer_email']],
            body=f"""
Hi {details['customer_name']},

Your booking status has been updated to: {new_status}.

📍 Pickup: {details['pickup']}
🏁 Dropoff: {details['dropoff']}
🕒 Time: {details['datetime']}
👨‍✈️ Driver: {driver_display}

Thank you for using Grab Student.
"""
        )

        msg.html = f"""
        <p>Hi {details['customer_name']},</p>
        <p>Your booking status has been updated to: 
        <b style="color: {'green' if new_status=='Completed' else 'red' if new_status=='Cancelled' else 'blue'};">
        {new_status}</b></p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background-color:{'green' if new_status=='Completed' else 'red' if new_status=='Cancelled' else '#f2f2f2'};">
                <th>Pickup</th>
                <th>Dropoff</th>
                <th>Time</th>
                <th>Driver</th>
            </tr>

            <tr>
                <td>{details['pickup']}</td>
                <td>{details['dropoff']}</td>
                <td>{details['datetime']}</td>
                <td>{driver_display}</td>
            </tr>
        </table>

        <p>Thank you for using Grab Student.</p>
        """

        Thread(target=send_async_email, args=(app, msg)).start()
    except Exception as e:
        print("Error sending email:", e)

    flash(f"✅ Booking status updated to {new_status}.")
    return redirect(url_for('driver_bookings'))

#------------------ ADMIN DASHBOARD -----------------

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    status_filter = request.args.get('status')  # Get status from query parameter

    cursor = db.cursor(dictionary=True)

    # Overview counts
    cursor.execute("SELECT COUNT(*) as total FROM booking")
    total_bookings = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as completed FROM booking WHERE status='Completed'")
    completed_bookings = cursor.fetchone()['completed']

    cursor.execute("SELECT COUNT(*) as pending FROM booking WHERE status='Pending'")
    pending_bookings = cursor.fetchone()['pending']

    cursor.execute("SELECT COUNT(*) as cancelled FROM booking WHERE status='Cancelled'")
    cancelled_bookings = cursor.fetchone()['cancelled']

    cursor.execute("SELECT SUM(total_amount) as total_profit FROM booking WHERE status='Completed'")
    total_profit = cursor.fetchone()['total_profit'] or 0

    # Recent bookings with optional status filter
    query = """
        SELECT b.id, b.name, b.pickup, b.dropoff, b.datetime, b.status, d.name as driver_name
        FROM booking b
        LEFT JOIN drivers d ON b.driver_id = d.driver_id
    """
    params = []
    if status_filter:
        query += " WHERE b.status=%s"
        params.append(status_filter)
    query += " ORDER BY b.datetime DESC LIMIT 5"

    cursor.execute(query, tuple(params))
    recent_bookings = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin.html',
        total_bookings=total_bookings,
        completed_bookings=completed_bookings,
        pending_bookings=pending_bookings,
        cancelled_bookings=cancelled_bookings,
        total_profit=total_profit,
        recent_bookings=recent_bookings,
        status_filter=status_filter  # pass to HTML for active tab
    )


# ----------------- ADMIN: Manage Bookings -----------------
@app.route('/admin/bookings')
def admin_bookings():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    status = request.args.get('status')
    driver_id = request.args.get('driver_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = """
        SELECT b.id, b.pickup, b.dropoff, b.datetime, b.status, b.payment_status, b.total_amount,
               u.name AS customer_name, u.email, b.driver_id
        FROM booking b
        LEFT JOIN users u ON b.user_id = u.id
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND b.status=%s"
        params.append(status)
    if driver_id:
        query += " AND b.driver_id=%s"
        params.append(driver_id)
    if date_from:
        query += " AND DATE(b.datetime) >= %s"
        params.append(date_from)
    if date_to:
        query += " AND DATE(b.datetime) <= %s"
        params.append(date_to)

    query += " ORDER BY b.datetime DESC"

    cursor = db.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    bookings = cursor.fetchall()

    # Fetch all drivers for the filter dropdown
    cursor.execute("SELECT driver_id, name FROM drivers")
    drivers = cursor.fetchall()

    cursor.close()
    return render_template('admin_bookings.html', bookings=bookings, drivers=drivers)


# Edit booking
@app.route('/admin/bookings/edit/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM booking WHERE id=%s", (booking_id,))
    booking = cursor.fetchone()

    if request.method == 'POST':
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        datetime_input = request.form['datetime']
        status = request.form['status']
        payment_status = request.form['payment_status']
        payment_amount = request.form['total_amount'] or 0

        cursor.execute("""
            UPDATE booking
            SET pickup=%s, dropoff=%s, datetime=%s, status=%s,
                payment_status=%s, total_amount=%s
            WHERE id=%s
        """, (pickup, dropoff, datetime_input, status, payment_status, payment_amount, booking_id))
        db.commit()
        cursor.close()
        flash("✅ Booking updated successfully!")
        return redirect(url_for('admin_bookings'))

    cursor.close()
    return render_template('edit_booking.html', booking=booking)



# Delete booking
@app.route('/admin/bookings/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM booking WHERE id=%s", (booking_id,))
    db.commit()
    cursor.close()
    flash("✅ Booking deleted successfully!")
    return redirect(url_for('admin_bookings'))

# ----------------- ADMIN: Manage Users -----------------
# Admin: View users & drivers
@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip()  # get search input

    cursor = db.cursor(dictionary=True)

    # Fetch customers (excluding admins)
    if search_query:
        cursor.execute(
            "SELECT id, name, email, user_type FROM users WHERE user_type != 'admin' AND (name LIKE %s OR email LIKE %s)",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute(
            "SELECT id, name, email, user_type FROM users WHERE user_type != 'admin'"
        )
    users = cursor.fetchall()

    # Fetch drivers
    if search_query:
        cursor.execute(
            "SELECT driver_id, name, email FROM drivers WHERE name LIKE %s OR email LIKE %s",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute(
            "SELECT driver_id, name, email FROM drivers"
        )
    drivers = cursor.fetchall()

    cursor.close()

    return render_template('admin_users.html', users=users, drivers=drivers)



# Admin: Edit user/driver 
@app.route('/admin/users/edit/<int:user_id>/<user_type>', methods=['GET','POST'])
def edit_user(user_id, user_type):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)

    # Fetch existing record
    if user_type == 'driver':
        cursor.execute("SELECT * FROM drivers WHERE driver_id=%s", (user_id,))
    else:
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    record = cursor.fetchone()

    if not record:
        cursor.close()
        flash("❌ Record not found!")
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form.get('password')  # optional

        # Update query
        if password:  # only update password if provided
            if user_type == 'driver':
                cursor.execute(
                    "UPDATE drivers SET name=%s, email=%s, password=%s WHERE driver_id=%s",
                    (name, email, password, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                    (name, email, password, user_id)
                )
        else:  # update without password
            if user_type == 'driver':
                cursor.execute(
                    "UPDATE drivers SET name=%s, email=%s WHERE driver_id=%s",
                    (name, email, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s WHERE id=%s",
                    (name, email, user_id)
                )

        db.commit()
        cursor.close()
        flash("✅ Record updated successfully!")
        return redirect(url_for('admin_users'))

    cursor.close()
    return render_template('edit_user.html', record=record, user_type=user_type)



# Admin: Delete user/driver
@app.route('/admin/users/delete/<int:user_id>/<user_type>', methods=['POST'])
def delete_user(user_id, user_type):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor()
    if user_type == 'driver':
        cursor.execute("DELETE FROM drivers WHERE driver_id=%s", (user_id,))
    else:
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    db.commit()
    cursor.close()
    flash("✅ User/Driver deleted successfully!")
    return redirect(url_for('admin_users'))

# Admin: Edit My Profile
@app.route('/admin/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    admin = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Update fields
        if password:
            cursor.execute("UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                           (name, email, password, session['user_id']))
        else:
            cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s",
                           (name, email, session['user_id']))

        db.commit()
        cursor.close()
        flash("✅ Profile updated successfully!")
        return redirect(url_for('admin_dashboard'))

    cursor.close()
    return render_template('edit_profile.html', admin=admin)

# ----------------- CUSTOMER DASHBOARD -----------------

@app.route('/customer')
@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    status_filter = request.args.get('status')  # ?status= filter

    cursor = db.cursor(dictionary=True)

    # Fetch bookings with optional status filter
    if status_filter:
        cursor.execute("""
            SELECT b.*, 
                   f.id AS feedback_id
            FROM booking b
            LEFT JOIN feedback f ON f.booking_id = b.id AND f.user_id = %s
            WHERE b.user_id=%s AND b.status=%s
            ORDER BY b.datetime DESC
        """, (session['user_id'], session['user_id'], status_filter))
    else:
        cursor.execute("""
            SELECT b.*, 
                   f.id AS feedback_id
            FROM booking b
            LEFT JOIN feedback f ON f.booking_id = b.id AND f.user_id = %s
            WHERE b.user_id=%s
            ORDER BY b.datetime DESC
        """, (session['user_id'], session['user_id']))

    bookings_raw = cursor.fetchall()

    # Add a boolean flag for each booking to indicate feedback exists
    bookings = []
    for b in bookings_raw:
        b['has_feedback'] = b['feedback_id'] is not None
        bookings.append(b)

    # Fetch previous feedbacks
    cursor.execute("""
        SELECT f.*, b.pickup, b.dropoff, b.datetime
        FROM feedback f
        JOIN booking b ON f.booking_id = b.id
        WHERE f.user_id=%s
        ORDER BY f.created_at DESC
    """, (session['user_id'],))
    feedbacks = cursor.fetchall()

    cursor.close()
    return render_template(
        'customer_dashboard.html',
        bookings=bookings,
        feedbacks=feedbacks,
        status_filter=status_filter
    )



# Cancel booking
@app.route('/customer/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "UPDATE booking SET status='Cancelled' WHERE id=%s AND user_id=%s AND status NOT IN ('Completed', 'Cancelled')",
        (booking_id, session['user_id'])
    )
    db.commit()
    cursor.close()

    flash("✅ Booking cancelled successfully.")
    return redirect(url_for('customer_dashboard'))


@app.route('/feedback', methods=['GET', 'POST'])
def feedback_index():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    # Get all completed bookings for this user
    cursor.execute("SELECT * FROM booking WHERE user_id=%s AND status='Completed'", (session['user_id'],))
    bookings = cursor.fetchall()

    # Get all previous feedbacks
    cursor.execute("""
        SELECT f.*, b.pickup, b.dropoff, b.datetime
        FROM feedback f
        JOIN booking b ON f.booking_id = b.id
        WHERE f.user_id=%s
        ORDER BY f.created_at DESC
    """, (session['user_id'],))
    feedbacks = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        booking_id = request.form['booking_id']
        rating = request.form['rating']
        comment = request.form['comment']

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO feedback (user_id, booking_id, rating, comment, created_at) VALUES (%s,%s,%s,%s,NOW())",
            (session['user_id'], booking_id, rating, comment)
        )
        db.commit()
        cursor.close()
        flash("✅ Feedback submitted successfully!")
        return redirect(url_for('feedback'))

    return render_template('feedback.html', bookings=bookings, feedbacks=feedbacks)

# Provide feedback
@app.route('/customer/feedback/<int:booking_id>', methods=['GET', 'POST'])
def feedback_booking(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM booking WHERE id=%s AND user_id=%s", (booking_id, session['user_id']))
    booking = cursor.fetchone()

    if not booking:
        cursor.close()
        flash("❌ Booking not found.")
        return redirect(url_for('customer_dashboard'))

    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']

        cursor.execute(
            "INSERT INTO feedback (booking_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)",
            (booking_id, session['user_id'], rating, comment)
        )
        db.commit()
        cursor.close()

        flash("✅ Feedback submitted. Thank you!")
        return redirect(url_for('customer_dashboard'))

    cursor.close()
    return render_template('feedback.html', booking=booking)


# Booking detail
@app.route('/customer/booking/<int:booking_id>')
def booking_detail(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, d.name AS driver_name
        FROM booking b
        LEFT JOIN drivers d ON b.driver_id = d.driver_id
        WHERE b.id = %s AND b.user_id = %s
    """, (booking_id, session['user_id']))
    booking = cursor.fetchone()
    cursor.close()

    if not booking:
        flash("❌ Booking not found.")
        return redirect(url_for('customer_dashboard'))

    return render_template('booking_detail.html', booking=booking)


# ----------------- EDIT FEEDBACK -----------------
@app.route('/edit_feedback/<int:feedback_id>', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    cursor = db.cursor(dictionary=True)

    # Get current feedback for display
    cursor.execute("SELECT * FROM feedback WHERE id = %s", (feedback_id,))
    feedback = cursor.fetchone()

    if request.method == 'POST':
        action = request.form.get("action")

        if action == "update":
            rating = request.form["rating"]
            comment = request.form["comment"]

            cursor.execute("""
                UPDATE feedback
                SET rating = %s, comment = %s
                WHERE id = %s
            """, (rating, comment, feedback_id))
            db.commit()
            flash("✅ Feedback updated successfully.")
            return redirect(url_for("customer_dashboard"))

        elif action == "delete":
            cursor.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
            db.commit()
            flash("🗑️ Feedback deleted successfully.")
            return redirect(url_for("customer_dashboard"))

    cursor.close()
    return render_template("edit_feedback.html", feedback=feedback)



# ----------------- DELETE FEEDBACK -----------------
@app.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM feedback WHERE feedback_id=%s AND user_id=%s", 
                   (feedback_id, session['user_id']))
    db.commit()
    cursor.close()

    flash("🗑️ Feedback deleted successfully.")
    return redirect(url_for('customer_dashboard'))

# ----------------- ADMIN: View All Feedback -----------------
@app.route('/admin/feedback')
def admin_feedbacks():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            f.id AS feedback_id,
            f.rating,
            f.comment,
            f.created_at,
            cu.name AS customer_name,
            d.name AS driver_name
        FROM feedback f
        JOIN booking b ON f.booking_id = b.id
        JOIN users cu ON f.user_id = cu.id
        LEFT JOIN drivers d ON d.driver_id = b.driver_id
        ORDER BY f.created_at DESC
    """)


    feedbacks = cursor.fetchall()
    cursor.close()

    return render_template('admin_feedbacks.html', feedbacks=feedbacks)


# ----------------- ADMIN DELETE FEEDBACK -----------------
@app.route('/admin/delete_feedback/<int:feedback_id>', methods=['POST'])
def admin_delete_feedback(feedback_id):
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash("⚠️ Admin access required.")
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM feedback WHERE id=%s", (feedback_id,))
    db.commit()
    cursor.close()

    flash("🗑️ Feedback deleted successfully.")
    return redirect(url_for('admin_feedbacks'))

# ----------------- CUSTOMER PAYMENTS -----------------
@app.route('/customer/payments', methods=['GET'])
def payments():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    user_id = session['user_id']
    status = request.args.get('status')   # "Paid" or "Unpaid" from the tabs
    search = request.args.get('search')

    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM booking WHERE user_id = %s"
    params = [user_id]

    # ✅ Map "Unpaid" → "Pending"
    if status == "Paid":
        query += " AND payment_status = 'Paid'"
    elif status == "Unpaid":
        query += " AND payment_status = 'Pending'"

    if search:
        query += " AND (pickup LIKE %s OR dropoff LIKE %s)"
        search_like = f"%{search}%"
        params.extend([search_like, search_like])

    query += " ORDER BY datetime DESC"
    cursor.execute(query, params)
    bookings = cursor.fetchall()
    cursor.close()

    return render_template(
        'payments.html',
        bookings=bookings,
        payment_filter=status,   # 👈 match your HTML variable name
        search=search
    )



# ----------------- CUSTOMER: Pay Booking -----------------
@app.route('/customer/pay_booking/<int:booking_id>', methods=['POST'])
def pay_booking(booking_id):
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash("⚠️ Customer access required.")
        return redirect(url_for('login'))

    amount = request.form.get('amount')
    payment_method = request.form.get('payment_method')

    cursor = db.cursor()
    cursor.execute("""
        UPDATE booking
        SET total_amount=%s, payment_status='Paid', payment_method=%s
        WHERE id=%s AND user_id=%s
    """, (amount, payment_method, booking_id, session['user_id']))
    db.commit()
    cursor.close()

    flash(f"✅ Payment of RM{amount} via {payment_method} recorded successfully!")
    return redirect(url_for('payments'))  # redirect back to payments page


# ----------------- RUN SERVER -----------------

if __name__ == '__main__':
    app.run(debug=True)


