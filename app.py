from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import app, db, Admin, Company, Student, PlacementDrive, Application
import os

#Secret ke for session
app.secret_key = 'placement_secret_key'

@app.route('/')
def index():
    view = request.args.get('view', 'default')
    return render_template('index.html', view=view)

@app.route('/student_register', methods = ['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        skills = request.form.get('skills')

        new_student = Student(name=name, email=email, password=password, skills=skills)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash("Student already exists. Please try again.", 'danger')
    return render_template('authen/student_reg.html')

@app.route('/company_register', methods = ['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        website = request.form.get('website')
        hr_contact = request.form.get('hr_contact')

        new_company = Company(name=name, email=email, password=password, website=website, hr_contact=hr_contact, status='Pending')
        try:
            db.session.add(new_company)
            db.session.commit()
            flash('Registration successful! Please wait for admin approval.', 'success')
            return redirect(url_for('login'))
        except:
            flash("Company already exists. Please try again.", 'danger')
    return render_template('authen/company_reg.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username = login_id, password = password).first()
        if admin:
            session['user_id'] = admin.id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        
        student = Student.query.filter_by(email=login_id, password=password).first()
        if student:
            session['user_id'] = student.id
            session['role'] = 'student'
            return redirect(url_for('student_dashboard'))
        
        company = Company.query.filter_by(email=login_id, password=password).first()
        if company:
            if company.status == 'Approved':
                session['user_id'] = company.id
                session['role'] = 'company'
                return redirect(url_for('company_dashboard'))
            else:
                flash('Your account is pending approval. Please wait for admin approval.', 'warning')
        
        else:
            flash("Invalid credentials. Please try again.", 'danger')
    return render_template('index.html', view='login')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'admin':
        return render_template('admin/admin_dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' in session and session['role'] == 'student':
        return render_template('student/student_dashboard.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/company_dashboard')
def company_dashboard():
    if 'user_id' in session and session['role'] == 'company':
        return render_template('company/company_dashboard.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
            
