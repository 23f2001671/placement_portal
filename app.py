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
        description = request.form.get('description')

        new_company = Company(name=name, email=email, password=password, website=website, hr_contact=hr_contact, description=description, status='Pending')
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
            if student.is_active == True:
                session['user_id'] = student.id
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))
            else:
                flash('Your account is deactivated.', 'danger')
                return redirect(url_for('login'))
        
        
        company = Company.query.filter_by(email=login_id, password=password).first()
        if company:
            if company.is_active == True:
                if company.status == 'Approved':
                    session['user_id'] = company.id
                    session['role'] = 'company'
                    return redirect(url_for('company_dashboard'))
                elif company.status == 'Pending':
                    flash('Your account is pending approval. Please wait for admin approval.', 'warning')
                else:
                    flash('Your account has been rejected. Please contact support.', 'danger')
            else:
                flash('Your account is deactivated.', 'danger')
                return redirect(url_for('login'))
        else:
            flash("Invalid credentials or Account not found. Please try again.", 'danger')
    return render_template('index.html', view='login')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    student_search = request.args.get('student_search', '').strip()
    company_search = request.args.get('company_search', '').strip()

    stats = {
        'total_students': Student.query.filter(Student.is_active == True).count(),
        'total_companies': Company.query.filter(Company.is_active == True).count(),
        'pending_companies': Company.query.filter_by(status='Pending', is_active=True).count(),
    }

    student_query = Student.query
    if student_search:
        student_query = student_query.filter(Student.name.contains(student_search) | Student.id.contains(student_search))
    students = student_query.filter(Student.is_active == True).all()

    company_query = Company.query.filter_by(status = "Approved")
    if company_search:
        company_query = company_query.filter(Company.name.contains(company_search) | Company.id.contains(company_search))
    approved_companies = company_query.filter(Company.is_active == True).all()
    pending_companies = Company.query.filter_by(status='Pending', is_active=True).all()
    pending_drives = PlacementDrive.query.filter_by(status='Pending', is_active=True).all()
    ongoing_drives = PlacementDrive.query.filter_by(status='Approved', is_active=True).all()
    all_applications = Application.query.filter(Application.is_active == True).all()

    return render_template('admin/admin_dashboard.html',
                           student_search=student_search,
                           company_search=company_search, 
                           stats=stats, 
                           students=students, 
                           approved=approved_companies, 
                           pending=pending_companies,
                           pending_drives=pending_drives,
                           ongoing_drives=ongoing_drives,
                           applications=all_applications)

@app.route('/deactivate/<string:type>/<int:id>')
def deactivate_account(type, id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    try:
        if type == 'student':
            student = Student.query.get(id)
            if student:
                student.is_active = False
                db.session.commit()
                flash('Student account deactivated successfully.', 'success')
            else:
                flash('Student not found.', 'danger')

        elif type == 'company':
            company = Company.query.get(id)
            if company:
                company.is_active = False
                for drive in company.drives:
                    drive.is_active = False
                    for application in drive.applications:
                        application.is_active = False
                db.session.commit()
                flash('Company and its drives deactivated successfully.', 'success')
            else:
                flash('Company not found.', 'danger')

        else:
            flash('Invalid account type.', 'danger')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deactivating the account.', 'danger')

    return redirect(url_for('view_history'))

@app.route('/activate/<string:type>/<int:id>')
def activate_account(type, id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    try:
        if type == 'student':
            student = Student.query.get(id)
            if student:
                student.is_active = True
                db.session.commit()
                flash('Student account activated successfully.', 'success')
            else:
                flash('Student not found.', 'danger')

        elif type == 'company':
            company = Company.query.get(id)
            if company:
                company.is_active = True
                for drive in company.drives:
                    drive.is_active = True
                    for application in drive.applications:
                        application.is_active = True
                db.session.commit()
                flash('Company and its drives activated successfully.', 'success')
            else:
                flash('Company not found.', 'danger')

        else:
            flash('Invalid account type.', 'danger')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while activating the account.', 'danger')

    return redirect(url_for('view_history'))

@app.route('/delete/<string:type>/<int:id>')
def delete_account(type, id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    try:
        if type == 'student':
            student = Student.query.get(id)
            if student:
                db.session.delete(student)
                db.session.commit()
                flash('Student account deleted successfully.', 'success')
            else:
                flash('Student not found.', 'danger')

        elif type == 'company':
            company = Company.query.get(id)
            if company:
                for drive in company.drives:
                    for application in drive.applications:
                        db.session.delete(application)
                    db.session.delete(drive)
                db.session.delete(company)
                db.session.commit()
                flash('Company and its drives deleted successfully.', 'success')
            else:
                flash('Company not found.', 'danger')

        else:
            flash('Invalid account type.', 'danger')
    
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the account.', 'danger')

    return redirect(url_for('view_history'))

@app.route('/view_history')
def view_history():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    students = Student.query.all()
    company = Company.query.all()
    drives = PlacementDrive.query.all()
    applications = Application.query.all()
    
    return render_template('admin/view_history.html', students=students, company=company, drives=drives, applications=applications)

@app.route('/approve_company/<int:id>')
def approve_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    company = Company.query.get(id)
    if company:
        company.status = 'Approved'
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_company/<int:id>')
def reject_company(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    company = Company.query.get(id)
    if company:
        company.status = 'Rejected'
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/approve_drive/<int:id>')
def approve_drive(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    drive = PlacementDrive.query.get(id)
    if drive:
        drive.status = 'Approved'
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_drive/<int:id>')
def reject_drive(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    drive = PlacementDrive.query.get(id)
    if drive:
        drive.status = 'Rejected'
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    else:
        return render_template('student/student_dashboard.html')
    
@app.route('/company_dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect(url_for('login'))
        
    else:
        return render_template('company/company_dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
