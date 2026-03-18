AttendIQ – GPS Verified Attendance System

A web-based attendance system where employees can Check-In and Check-Out at a shop location using GPS verification and a selfie image.


Features

-  GPS location verification — attendance only allowed within 100 meters of shop
-  Selfie capture using device camera
-  Check-In and Check-Out functionality
-  Prevents multiple check-ins per day
-  Attendance history with selfie thumbnails
-  Real-time distance display with progress bar
-  Mobile responsive UI
-  Django Admin panel to view all records
-  Selfie images stored in media folder

---



Tech Stack
|-------|-----------|
| Backend | Python + Django |
| Database | MySQL |
| Frontend | HTML + CSS + JavaScript |
| Image Storage | Django Media Files |




Setup Instructions

 Step 1 — Install dependencies

pip install Django
pip install mysqlclient
pip install Pillow


 Step 2 — Create MySQL database
bash
mysql -u root -p

sql
CREATE DATABASE attendiq_db;
EXIT;


step 3— Configure database in settings.py
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
bash
python manage.py makemigrations
python manage.py migrate


 Step 5 — Create admin user (optional)
bash
python manage.py createsuperuser


 Step 6 — Start server
bash
python manage.py runserver


 Step 7 — Open in browser

http://localhost:8000


---
Database Schema----

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
    checkout_image VARCHAR(100)  NULL
);



API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | / | Login page |
| GET | /dashboard/ | Main dashboard |
| GET | /history/ | Attendance history |
| GET | /logout/ | Logout user |
| POST | /attendance/checkin/ | Mark check-in |
| POST | /attendance/checkout/ | Mark check-out |
| GET | /attendance/today/<user_id>/ | Today's status |
| GET | /attendance/user/<user_id>/ | All records |






Business Rules

- Employee can only mark attendance within *100 meters* of the shop
- Selfie is required for both Check-In and Check-Out
- Only one Check-In per day per employee
- Check-Out is only possible after a successful Check-In
- Distance calculated using Haversine formula







