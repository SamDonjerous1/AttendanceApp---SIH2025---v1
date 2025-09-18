from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import datetime, os

# -------------------
# Flask + DB setup
# -------------------
app = Flask(__name__)

# Use DATABASE_URL from environment (Render provides this for Postgres)
db_url = os.getenv("DATABASE_URL", "sqlite:///System.db")  # fallback for local dev
# Render's Postgres URLs often start with "postgres://", SQLAlchemy expects "postgresql://"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------
# Models
# -------------------
class College(db.Model):
    __tablename__ = "college"
    CollegeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Roll_no = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    College_Email = db.Column(db.String(100), unique=True, nullable=False)
    Role = db.Column(db.String(20), nullable=False)  # Student / Teacher
    Password = db.Column(db.String(200), nullable=False)


class Course(db.Model):
    __tablename__ = "course"
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Year = db.Column(db.String(10), primary_key=True)
    Session = db.Column(db.String(10), primary_key=True)
    Class = db.Column(db.String(20), primary_key=True)
    Roll_no = db.Column(db.String(20), db.ForeignKey('user.Roll_no'), primary_key=True)
    Subject = db.Column(db.String(50), primary_key=True)


class Attendance(db.Model):
    __tablename__ = "attendance"
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Year = db.Column(db.String(10), primary_key=True)
    Session = db.Column(db.String(10), primary_key=True)
    Class = db.Column(db.String(20), primary_key=True)
    Subject = db.Column(db.String(50), primary_key=True)
    Roll_no = db.Column(db.String(20), db.ForeignKey('user.Roll_no'), primary_key=True)
    No_of_Total_day = db.Column(db.Integer, default=0)
    No_of_days_present = db.Column(db.Integer, default=0)
    Attendance_Percent = db.Column(db.Float, default=0.0)
    Today_PresentOrAbsent = db.Column(db.Boolean, default=False)


class TimeTable(db.Model):
    __tablename__ = "timetable"
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Year = db.Column(db.String(10), primary_key=True)
    Session = db.Column(db.String(10), primary_key=True)
    Class = db.Column(db.String(20), primary_key=True)
    Day = db.Column(db.String(20), primary_key=True)
    Time = db.Column(db.String(10), primary_key=True)
    Duration = db.Column(db.String(10))
    Subject = db.Column(db.String(50))
    Venue = db.Column(db.String(50))


class Holiday(db.Model):
    __tablename__ = "holiday"
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    date = db.Column(db.String(20), primary_key=True)  # YYYY-MM-DD
    Occasion = db.Column(db.String(100))


# -------------------
# API Endpoints
# -------------------

@app.route('/')
def home():
    return {"message": "Attendance Backend Running 🚀"}


@app.route('/add_college', methods=['POST'])
def add_college():
    data = request.json
    name = data['name']

    # Check if college already exists
    existing = College.query.filter_by(Name=name).first()
    if existing:
        return jsonify({"success": False, "message": "College already exists"})

    # Add new college
    new_college = College(Name=name)
    db.session.add(new_college)
    db.session.commit()

    return jsonify({"success": True, "collegeId": new_college.CollegeId})


# -------------------
# Get College ID by name
# -------------------

@app.route('/get_colleges', methods=['GET'])
def get_colleges():
    colleges = College.query.all()
    college_names = [c.Name for c in colleges]
    return jsonify({"colleges": college_names})

@app.route('/get_college_id', methods=['POST'])
def get_college_id():
    data = request.json
    name = data['name']

    college = College.query.filter_by(Name=name).first()
    if college:
        return jsonify({"collegeId": college.CollegeId})
    else:
        return jsonify({"collegeId": None, "message": "College not found"})

# ✅ Add a new user
@app.route('/new_user', methods=['POST'])
def new_user():
    data = request.json
    user = User.query.filter_by(CollegeId=data['collegeId'], Roll_no=data['rollNo']).first()
    if user:
        return jsonify({"success": False, "message": "User already exists"})

    hashed_pw = generate_password_hash(data['plainTextPassword'])
    user = User(
        CollegeId=data['collegeId'],
        Roll_no=data['rollNo'],
        Name=data['name'],
        College_Email=data['email'],
        Role=data['role'],
        Password=hashed_pw
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "message": "User added"})


# ✅ Existing user check (login)
@app.route('/existing_user', methods=['POST'])
def existing_user():
    data = request.json
    user = User.query.filter_by(CollegeId=data['collegeId'], Roll_no=data['rollNo']).first()
    if not user or not check_password_hash(user.Password, data['plainTextPassword']):
        return jsonify({"success": False})
    return jsonify({"success": True})


# ✅ View courses
@app.route('/view_courses', methods=['POST'])
def view_courses():
    data = request.json
    courses = Course.query.filter_by(
        CollegeId=data['collegeId'],
        Year=data['year'],
        Session=data['session'],
        Roll_no=data['rollNo']
    ).all()
    return jsonify([c.Subject for c in courses])

@app.route('/get_all_classes', methods=['POST'])
def get_all_classes():
    data = request.json
    college_id = data['collegeId']
    year = data['year']
    session = data['session']
    roll_no = data['rollNo']

    # Query courses for the student and get unique classes
    courses = Course.query.filter_by(
        CollegeId=college_id,
        Year=year,
        Session=session,
        Roll_no=roll_no
    ).all()

    classes = list({c.Class for c in courses})  # set to get unique classes

    return jsonify({"classes": classes})


# ✅ View attendance per subject
@app.route('/view_attendance', methods=['POST'])
def view_attendance():
    data = request.json
    records = Attendance.query.filter_by(
        CollegeId=data['collegeId'],
        Roll_no=data['rollNo'],
        Year=data['year'],
        Session=data['session']
    ).all()  # no Class filter

    result = []
    for rec in records:
        result.append({
            "Class": rec.Class,  # include class in response for clarity
            "Subject": rec.Subject,
            "TotalDays": rec.No_of_Total_day,
            "DaysPresent": rec.No_of_days_present,
            "AttendancePercent": rec.Attendance_Percent
        })
    return jsonify(result)


# ✅ Mark attendance
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    record = Attendance.query.filter_by(
        CollegeId=data['collegeId'],
        Roll_no=data['rollNo'],
        Year=data['year'],
        Session=data['session'],
        Class=data['className'],
        Subject=data['subject']
    ).first()
    if not record:
        return jsonify({"success": False, "message": "Record not found"})
    record.Today_PresentOrAbsent = data['mark']
    db.session.commit()
    return jsonify({"success": True, "message": "Attendance marked"})


# ✅ View timetable
@app.route('/view_timetable', methods=['POST'])
def view_timetable():
    data = request.json
    courses = Course.query.filter_by(
        CollegeId=data['collegeId'],
        Year=data['year'],
        Session=data['session'],
        Roll_no=data['rollNo']
    ).all()
    subjects = [c.Subject for c in courses]

    timetable = TimeTable.query.filter(
        TimeTable.CollegeId == data['collegeId'],
        TimeTable.Year == data['year'],
        TimeTable.Session == data['session'],
        TimeTable.Subject.in_(subjects)
    ).all()

    result = []
    for t in timetable:
        result.append({
            "Day": t.Day,
            "Time": t.Time,
            "Duration": t.Duration,
            "Subject": t.Subject,
            "Venue": t.Venue
        })
    return jsonify(result)


# ✅ Check holiday
@app.route('/is_holiday', methods=['POST'])
def is_holiday():
    data = request.json
    holiday = Holiday.query.filter_by(CollegeId=data['collegeId'], date=data['date']).first()
    if holiday:
        return jsonify({"isHoliday": True, "Occasion": holiday.Occasion})
    return jsonify({"isHoliday": False})


# -------------------
# Scheduler: Update Attendance at midnight
# -------------------
def update_attendance_midnight():
    with app.app_context():
        all_records = Attendance.query.all()
        for rec in all_records:
            rec.No_of_Total_day += 1
            if rec.Today_PresentOrAbsent:
                rec.No_of_days_present += 1
            rec.Attendance_Percent = (
                rec.No_of_days_present / rec.No_of_Total_day
            ) * 100 if rec.No_of_Total_day > 0 else 0
            rec.Today_PresentOrAbsent = False  # reset for next day
        db.session.commit()
        print(f"[{datetime.datetime.now()}] Attendance updated ✅")


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_attendance_midnight, trigger="cron", hour=0, minute=0)  # every midnight
scheduler.start()

# -------------------
# Run App
# -------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
