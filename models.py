from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    website = db.Column(db.String(100))
    hr_contact = db.Column(db.String(15))
    status = db.Column(db.String(20), default='Pending')
    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade="all, delete-orphan")

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    skills = db.Column(db.String(200))
    resume_path = db.Column(db.String(200))
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    eligibility= db.Column(db.Text)
    deadline = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Pending')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    applications = db.relationship('Application', backref='drive', lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied')
    date_applied = db.Column(db.DateTime, default=datetime.now(timezone.utc))

def create_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            new_admin = Admin(username='admin', password='admin123')
            db.session.add(new_admin)
            db.session.commit()
        print("Database created successfully.")

if __name__ == '__main__':
    create_db()
    