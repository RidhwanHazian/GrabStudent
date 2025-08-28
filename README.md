# GrabStudent

GrabStudent is a web-based platform designed to streamline booking and feedback for students using Grab services. The application supports **Customers, Admins, and Drivers**.

- Customers can book rides, track statuses, and submit feedback.
- Drivers can view available bookings, select them, update statuses, and notify customers.
- Admins can oversee all bookings and feedback.

---

## Features

### 📋 Customer Dashboard

- **View All Bookings:** Customers can see all the bookings they have made.  
- **Status Filtering:** Easily filter bookings by status (Pending, Accepted, On the way, Completed, Cancelled).  
- **Booking Actions:**  
  - **Details:** View detailed information about each booking.  
  - **Delete:** Remove a booking if desired.  
  - **Give Feedback:** If a booking is completed and feedback has not yet been submitted, a "Give Feedback" button appears next to the details button.  
- **Feedback Section:**  
  - View all feedback previously submitted.  
  - Edit any existing feedback.  
- **Navbar (Top-Left):**  
  - **Dashboard:** Main bookings overview.  
  - **Make Booking:** Navigate to the booking form to create a new booking.  
  - **Payments:** View all bookings made and complete payment for them.  
  - **Logout:** Log out securely from the account.


### 🧑‍💻 Admin Dashboard

- **Dashboard Overview:**  
  - View total bookings with breakdown by status (Pending, Accepted, On the way, Completed, Cancelled).  
  - Track total profit.  
  - See all recent customer bookings.  
  - Visualize bookings by status with a pie chart (Pending, Cancelled, Completed).

- **Navbar:**  
  - **Manage Bookings:** Access all customer bookings.  
    - Filter by status, assigned driver, and date range.  
    - Delete bookings if necessary.  
  - **Manage Users/Drivers:**  
    - View all registered customers and drivers.  
    - Edit or delete user accounts.  
  - **Feedback:**  
    - View all customer feedback.  
    - Delete feedback if required.  
  - **Edit Profile:**  
    - Update the admin’s own profile details.  
  - **Logout:** Securely log out of the system.


### 🚗 Driver Dashboard

- **Available Bookings:**  
  - Upon login, drivers see all customer bookings that have not yet been assigned to another driver.  
  - Drivers can select a booking to take responsibility for it.

- **My Bookings:**  
  - Drivers can view all bookings they have accepted.  
  - Use a dropdown to filter bookings by status: Pending, Accepted, On the way, Completed, Cancelled.  
  - A button allows updating the booking status.  
  - When a booking status is updated, an email is sent to the customer notifying them of the change.

- **Navbar:**  
  - **Available Bookings:** Shows all unassigned bookings.  
  - **My Bookings:** Displays the driver’s accepted bookings with filtering options.  
  - **Logout:** Securely log out of the system.


---

## Technologies Used
- **Backend:** Python with Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL

---

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
> Or if `py` doesn’t work:
```bash
python app.py
```

The application will be accessible at: [http://localhost:5000](http://localhost:5000)

---

## Usage

### Customer Access
- Navigate to `/customer/dashboard` to view and manage bookings.
- Submit feedback on completed rides.

### Driver Access
- Navigate to `/driver` to view available bookings.
- Select a booking to take.
- Update the booking status using the dropdown in "Assigned Bookings".
- When a status is updated, an email is sent to the customer.

### Admin Access
- Navigate to `/admin/dashboard` to manage all customer bookings and feedback.

---

## Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request with your proposed changes.

---

## License
This project is licensed under the MIT License.
