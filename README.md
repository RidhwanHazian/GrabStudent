# GrabStudent

**GrabStudent** is a web-based platform designed to streamline the booking and feedback process for students using Grab services. The application allows students to:

- **Book rides** with specified pickup and dropoff locations.
- **Track booking statuses** (Pending, Accepted, On the way, Completed, Cancelled).
- **Provide feedback** on completed rides, including ratings and comments.

---

## Features

### 📋 Customer Dashboard

- **Booking Management**: View all bookings with their statuses and associated actions.
- **Feedback System**: Submit feedback for completed rides and edit existing feedback.
- **Status Filtering**: Filter bookings based on their current status.

### 🧑‍💻 Admin Dashboard

- **Booking Overview**: View all customer bookings and their statuses.
- **Feedback Management**: Access and manage customer feedback for each booking.

---

## Technologies Used

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL Server
- Flask
- Flask-MySQLdb

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/RidhwanHazian/GrabStudent.git
   cd GrabStudent
2. Setup database(e.g XAMPP), run the sql

3. Install dependencies, run in command promt
pip install -r requirements.txt

4. Run the application on command promt
py app.py

The application will be accessible at http://localhost:5000.
