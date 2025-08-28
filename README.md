# GrabStudent

GrabStudent is a web-based platform designed to streamline the booking and feedback process for students using Grab services. The application allows students to:

- Book rides with specified pickup and dropoff locations.
- Track booking statuses (Pending, Accepted, On the way, Completed, Cancelled).
- Provide feedback on completed rides, including ratings and comments.

## Features

### 📋 Customer Dashboard
- **Booking Management:** View all bookings with their statuses and associated actions.
- **Feedback System:** Submit feedback for completed rides and edit existing feedback.
- **Status Filtering:** Filter bookings based on their current status.

### 🧑‍💻 Admin Dashboard
- **Booking Overview:** View all customer bookings and their statuses.
- **Feedback Management:** Access and manage customer feedback for each booking.

## Technologies Used
- **Backend:** Python with Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL Server
- Flask
- Flask-MySQLdb

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/RidhwanHazian/GrabStudent.git
cd GrabStudent
```

#### 2. Create and Activate a Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```
> For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up the Database
1. Open MySQL or phpMyAdmin.
2. Create the database and import the schema:
```sql
CREATE DATABASE grabstudent;
USE grabstudent;
SOURCE grabstudent.sql;
```

#### 5. Configure the Application
Update the database connection in `app.py`:
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'grabstudent'
```

#### 6. Run the Application
```bash
py app.py
```
> Or if `py` doesn’t work, try:
```bash
python app.py
```

The application will be accessible at: [http://localhost:5000](http://localhost:5000)

## Usage
- **Customer Access:** Navigate to `/customer/dashboard` to view and manage bookings.
- **Admin Access:** Navigate to `/admin/dashboard` to manage all customer bookings and feedback.

## Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your proposed changes.

## License
This project is licensed under the MIT License.
