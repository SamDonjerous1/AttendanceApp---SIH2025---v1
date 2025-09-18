from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# College Table
class College(db.Model):
    __tablename__ = 'college'
    CollegeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(100), nullable=False)

# User Table
class User(db.Model):
    __tablename__ = 'user'
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Roll_no = db.Column(db.String(50), primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    College_Email = db.Column(db.String(120), unique=True, nullable=False)
    Role = db.Column(db.String(20), nullable=False)  # Student or Teacher
    Password = db.Column(db.String(100), nullable=False)

# Attendance Table
class Attendance(db.Model):
    __tablename__ = 'attendance'
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Roll_no = db.Column(db.String(50), db.ForeignKey('user.Roll_no'), primary_key=True)
    Year = db.Column(db.String(10), primary_key=True)
    Session = db.Column(db.String(10), primary_key=True)
    Class = db.Column(db.String(50), primary_key=True)
    Subject = db.Column(db.String(100), primary_key=True)
    No_of_Total_day = db.Column(db.Integer, default=0)
    No_of_days_present = db.Column(db.Integer, default=0)
    Attendance_Percent = db.Column(db.Float, default=0.0)
    Today_PresentOrAbsent = db.Column(db.String(10))  # Present/Absent

# Course Table
class Course(db.Model):
    __tablename__ = 'course'
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Year = db.Column(db.String(10), primary_key=True)
    Session = db.Column(db.String(10), primary_key=True)
    Class = db.Column(db.String(50), primary_key=True)
    Roll_no = db.Column(db.String(50), db.ForeignKey('user.Roll_no'), primary_key=True)
    Subject = db.Column(db.String(100), primary_key=True)

# Time Table
class TimeTable(db.Model):
    __tablename__ = 'timetable'
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    Year = db.Column(db.String(10), primary_key=True)
    Session = db.Column(db.String(10), primary_key=True)
    Class = db.Column(db.String(50), primary_key=True)
    Day = db.Column(db.String(20), primary_key=True)
    Time = db.Column(db.String(20), primary_key=True)
    Duration = db.Column(db.String(20))
    Subject = db.Column(db.String(100))
    Venue = db.Column(db.String(50))


# Holiday Table
class Holiday(db.Model):
    __tablename__ = 'holiday'
    CollegeId = db.Column(db.Integer, db.ForeignKey('college.CollegeId'), primary_key=True)
    date = db.Column(db.String(20), primary_key=True)
    Occasion = db.Column(db.String(100), nullable=False)
