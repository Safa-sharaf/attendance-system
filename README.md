AttendIQ – GPS + Face Verified Attendance System

A web-based attendance system where employees can Check-In and Check-Out at a shop location using GPS verification, selfie capture, and face recognition.

 Features

- GPS location verification — attendance only allowed within 100 meters of shop
- Face verification using OpenCV — system identifies employee from selfie
- Employee registration with face photo
- Check-In and Check-Out functionality
- Prevents multiple check-ins per day
- Attendance history with selfie thumbnails
- Real-time distance display with progress bar
- Mobile responsive UI
- Django Admin panel to view all records
- Selfie images stored in media folder



Tech Stack
|-------|-----------|
| Backend | Python + Django |
| Database | MySQL |
| Frontend | HTML + CSS + JavaScript |
| Face Recognition | OpenCV |
| Image Storage | Django Media Files |

---


Setup Instructions

 Step 1 — Install dependencies
bash
pip install Django
pip install mysqlclient
pip install Pillow
pip install opencv-python
pip install numpy

 Step 2 — Create MySQL database
bash
mysql -u root -p

sql
CREATE DATABASE attendiq_db;
EXIT;


Step 3 — Configure database in settings.py
python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'attendiq_db',
        'USER': 'root',
        'PASSWORD': 'your_password_here',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


Step 4 — Run migrations

python manage.py makemigrations
python manage.py migrate


Step 5 — Create admin user

python manage.py createsuperuser


 Step 6 — Start server

python manage.py runserver


 Step 7 — Open in browser

http://localhost:8000




 How to Use

 Step 1 — Register Employee

http://localhost:8000/register/

- Enter Employee ID, Full Name, Email
- Upload clear face photo OR take photo using camera
- Click Register

 Step 2 — Login

http://localhost:8000/

- Enter Employee ID and Full Name
- Click Continue to Dashboard

 Step 3 — Mark Attendance

http://localhost:8000/dashboard/

- GPS automatically detects your location
- Click Start Camera → Capture selfie
- System verifies your face with registered photo
- If face matches and within 100m → Check In enabled
- Click Check In → attendance saved!

---


Database Schema

Employee Table
sql
CREATE TABLE employee (
    id          BIGINT        PRIMARY KEY AUTO_INCREMENT,
    user_id     VARCHAR(50)   UNIQUE NOT NULL,
    user_name   VARCHAR(100)  NOT NULL,
    email       VARCHAR(254)  UNIQUE NOT NULL,
    face_image  VARCHAR(100)  NOT NULL,
    created_at  DATETIME      NOT NULL
);

 Attendance Table
sql
CREATE TABLE attendance (
    id             BIGINT        PRIMARY KEY AUTO_INCREMENT,
    user_id        VARCHAR(50)   NOT NULL,
    user_name      VARCHAR(100)  NOT NULL,
    date           DATE          NOT NULL,
    checkin_time   DATETIME      NULL,
    checkin_lat    DOUBLE        NULL,
    checkin_lng    DOUBLE        NULL,
    checkin_image  VARCHAR(100)  NULL,
    checkout_time  DATETIME      NULL,
    checkout_lat   DOUBLE        NULL,
    checkout_lng   DOUBLE        NULL,
    checkout_image VARCHAR(100)  NULL,
    face_verified  TINYINT(1)    DEFAULT 0
);

API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | / | Login page |
| GET | /register/ | Employee registration |
| GET | /dashboard/ | Main dashboard |
| GET | /history/ | Attendance history |
| GET | /logout/ | Logout user |
| POST | /attendance/checkin/ | Mark check-in with face verification |
| POST | /attendance/checkout/ | Mark check-out with face verification |
| GET | /attendance/today/<user_id>/ | Today's status |
| GET | /attendance/user/<user_id>/ | All records |


Business Rules

- Employee must be registered with face photo before logging in
- Employee can only mark attendance within 100 meters of the shop
- Face must match registered photo for attendance to be marked
- Selfie is required for both Check-In and Check-Out
- Only one Check-In per day per employee
- Check-Out is only possible after a successful Check-In
- Distance calculated using Haversine formula
- Face comparison done using OpenCV





