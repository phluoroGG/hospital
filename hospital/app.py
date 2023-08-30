from app_config import app, db
from model import *
from forms import *

import os
from datetime import datetime

from flask import request, render_template, redirect, url_for

from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from sqlalchemy import func, extract

per_page = 20

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    feedback = ''
    if request.method == 'POST':
        if request.form['cmd'] == 'Вход':
            u = db.session.query(User) \
                .filter(User.user_login == request.form['login']) \
                .filter(User.user_password == request.form['password']) \
                .one_or_none()
            if u is None:
                feedback = "Неверное имя пользователя или пароль"
            else:
                login_user(u)
                return redirect(request.args.get("next") or url_for('index'))

    return render_template('login.html', feedback=feedback)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter(User.user_id == int(user_id)).one_or_none()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.route('/department_list')
def department_list():
    departments = db.session.query(Department).order_by(Department.id).all()
    return render_template(
        "department_list.html",
        departments=departments
    )


@app.route('/doctor_list/<int:id>')
def doctor_list(id):
    if id == 0:
        department = None
        head = None
        doctors = db.session.query(Doctor).filter(Doctor.department_id == None).order_by(Doctor.id).all()
    else:
        department = db.session.query(Department).filter(Department.id == id).one_or_none()
        if department is None:
            return 'Not Found', 404
        head = db.session.query(Doctor).filter(Doctor.id == department.head).one_or_none()
        doctors = db.session.query(Doctor).filter(Doctor.department_id == department.id).order_by(Doctor.id).all()

    return render_template(
        "doctor_list.html",
        department=department,
        head=head,
        doctors=doctors
    )


@app.route('/patient_list')
@login_required
def patient_list():
    patients = db.session.query(Patient).order_by(Patient.id).all()

    return render_template(
        "patient_list.html",
        patients=patients
    )


@app.route('/price_list')
def price_list():
    services = db.session.query(Service).order_by(Service.id).all()

    return render_template(
        "price_list.html",
        services=services
    )


@app.route('/service_list', methods=['GET', 'POST'])
@login_required
def service_list():
    global per_page
    per_page = int(request.form.get("items", per_page))
    page = db.paginate(db.session.query(RenderedService).order_by(RenderedService.id), per_page=per_page)

    date = request.form.get("date")
    if date is None:
        if datetime.now().month == 1:
            year = datetime.now().year - 1
            month = 12
        else:
            year = datetime.now().year
            month = datetime.now().month - 1
    else:
        datestr = date.split("-")
        year = int(datestr[0])
        month = int(datestr[1])
    service_count = db.session.query(func.count(RenderedService.id)) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    sum_cost = db.session.query(func.sum(RenderedService.cost)) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    if month < 10:
        month = "0" + str(month)
    date = str(year) + "-" + str(month)

    return render_template(
        "service_list.html",
        page=page,
        date=date,
        service_count=service_count,
        sum_cost=sum_cost
    )


@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
def edit_department(id):
    if id == 0:
        d = Department()
    else:
        d = db.session.query(Department).filter(Department.id == id).one_or_none()
        if d is None:
            return 'Not Found', 404

    global per_page
    per_page = int(request.form.get("items", per_page))
    page = db.paginate(db.session.query(RenderedService).join(Doctor, RenderedService.doctor_id == Doctor.id)
                       .filter(Doctor.department_id == id).order_by(RenderedService.id), per_page=per_page)

    date = request.form.get("date")
    if date is None:
        if datetime.now().month == 1:
            year = datetime.now().year - 1
            month = 12
        else:
            year = datetime.now().year
            month = datetime.now().month - 1
    else:
        datestr = date.split("-")
        year = int(datestr[0])
        month = int(datestr[1])
    service_count = db.session.query(func.count(RenderedService.id)) \
        .filter(RenderedService.doctor_id == Doctor.id).filter(Doctor.department_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    sum_cost = db.session.query(func.sum(RenderedService.cost)) \
        .filter(RenderedService.doctor_id == Doctor.id).filter(Doctor.department_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    if month < 10:
        month = "0" + str(month)
    date = str(year) + "-" + str(month)

    form = DepartmentForm(request.form if request.method == "POST" else None, obj=d)

    if form.button_delete.data:
        db.session.query(Doctor).filter(Doctor.department_id == d.id).update({'department_id': None})
        db.session.delete(d)
        db.session.commit()
        return redirect(url_for('department_list'))

    if form.button_save.data and form.validate():
        form.populate_obj(d)
        db.session.add(d)
        db.session.commit()
        if id == 0:
            db.session.flush()
            return redirect(url_for('edit_department', id=d.id))

    return render_template(
        'edit_department.html',
        department=d,
        page=page,
        date=date,
        service_count=service_count,
        sum_cost=sum_cost,
        form=form
    )


@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    if id == 0:
        d = Doctor()
    else:
        d = db.session.query(Doctor).filter(Doctor.id == id).one_or_none()
        if d is None:
            return 'Not Found', 404

    global per_page
    per_page = int(request.form.get("items", per_page))
    page = db.paginate(db.session.query(RenderedService).filter(RenderedService.doctor_id == id)
                       .order_by(RenderedService.id), per_page=per_page)

    date = request.form.get("date")
    if date is None:
        if datetime.now().month == 1:
            year = datetime.now().year - 1
            month = 12
        else:
            year = datetime.now().year
            month = datetime.now().month - 1
    else:
        datestr = date.split("-")
        year = int(datestr[0])
        month = int(datestr[1])
    service_count = db.session.query(func.count(RenderedService.id)) \
        .filter(RenderedService.doctor_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    sum_cost = db.session.query(func.sum(RenderedService.cost)) \
        .filter(RenderedService.doctor_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    if month < 10:
        month = "0" + str(month)
    date = str(year) + "-" + str(month)

    form = DoctorForm(request.form if request.method == "POST" else None, obj=d)

    if form.button_delete.data:
        dep_id = d.department_id
        db.session.query(RenderedService).filter(RenderedService.doctor_id == d.id).update({'doctor_id': None})
        db.session.query(Department).filter(Department.head == d.id).update({'head': None})
        db.session.delete(d)
        db.session.commit()
        return redirect(url_for('doctor_list', id=dep_id))

    if form.button_save.data and form.validate():
        form.populate_obj(d)
        db.session.add(d)
        db.session.commit()
        if id == 0:
            db.session.flush()
            return redirect(url_for('edit_doctor', id=d.id))

    return render_template(
        'edit_doctor.html',
        doctor=d,
        page=page,
        date=date,
        service_count=service_count,
        sum_cost=sum_cost,
        form=form
    )


@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if id == 0:
        p = Patient()
    else:
        p = db.session.query(Patient).filter(Patient.id == id).one_or_none()
        if p is None:
            return 'Not Found', 404

    global per_page
    per_page = int(request.form.get("items", per_page))
    page = db.paginate(db.session.query(RenderedService).filter(RenderedService.patient_id == id)
                       .order_by(RenderedService.id), per_page=per_page)

    date = request.form.get("date")
    if date is None:
        if datetime.now().month == 1:
            year = datetime.now().year - 1
            month = 12
        else:
            year = datetime.now().year
            month = datetime.now().month - 1
    else:
        datestr = date.split("-")
        year = int(datestr[0])
        month = int(datestr[1])
    service_count = db.session.query(func.count(RenderedService.id)) \
        .filter(RenderedService.patient_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    sum_cost = db.session.query(func.sum(RenderedService.cost)) \
        .filter(RenderedService.patient_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    if month < 10:
        month = "0" + str(month)
    date = str(year) + "-" + str(month)

    form = PatientForm(request.form if request.method == "POST" else None, obj=p)

    if form.button_delete.data:
        db.session.query(RenderedService).filter(RenderedService.patient_id == p.id).update({'patient_id': None})
        db.session.delete(p)
        db.session.commit()
        return redirect(url_for('patient_list'))

    if form.button_save.data and form.validate():
        form.populate_obj(p)
        db.session.add(p)
        db.session.commit()
        if id == 0:
            db.session.flush()
            return redirect(url_for('edit_patient', id=p.id))

    return render_template(
        'edit_patient.html',
        patient=p,
        page=page,
        date=date,
        service_count=service_count,
        sum_cost=sum_cost,
        form=form
    )


@app.route('/edit_price_list/<int:id>', methods=['GET', 'POST'])
def edit_price_list(id):
    if id == 0:
        s = Service()
    else:
        s = db.session.query(Service).filter(Service.id == id).one_or_none()
        if s is None:
            return 'Not Found', 404

    global per_page
    per_page = int(request.form.get("items", per_page))
    page = db.paginate(db.session.query(RenderedService).filter(RenderedService.service_id == id)
                       .order_by(RenderedService.id), per_page=per_page)

    date = request.form.get("date")
    if date is None:
        if datetime.now().month == 1:
            year = datetime.now().year - 1
            month = 12
        else:
            year = datetime.now().year
            month = datetime.now().month - 1
    else:
        datestr = date.split("-")
        year = int(datestr[0])
        month = int(datestr[1])
    service_count = db.session.query(func.count(RenderedService.id)) \
        .filter(RenderedService.service_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    sum_cost = db.session.query(func.sum(RenderedService.cost)) \
        .filter(RenderedService.service_id == id) \
        .filter(extract('year', RenderedService.service_date) * 12 + extract('month', RenderedService.service_date)
                == year * 12 + month).all()[0][0]
    if month < 10:
        month = "0" + str(month)
    date = str(year) + "-" + str(month)

    form = PriceListForm(request.form if request.method == "POST" else None, obj=s)

    if form.button_delete.data:
        db.session.query(RenderedService).filter(RenderedService.service_id == s.id).update({'service_id': None})
        db.session.delete(s)
        db.session.commit()
        return redirect(url_for('price_list'))

    if form.button_save.data and form.validate():
        form.populate_obj(s)
        db.session.add(s)
        db.session.commit()
        if id == 0:
            db.session.flush()
            return redirect(url_for('edit_price_list', id=s.id))

    return render_template(
        'edit_price_list.html',
        service=s,
        page=page,
        date=date,
        service_count=service_count,
        sum_cost=sum_cost,
        form=form
    )


@app.route('/edit_service/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    if id == 0:
        s = RenderedService()
    else:
        s = db.session.query(RenderedService).filter(RenderedService.id == id).one_or_none()
        if s is None:
            return 'Not Found', 404

    form = ServiceForm(request.form if request.method == "POST" else None, obj=s)

    if form.button_delete.data:
        db.session.delete(s)
        db.session.commit()
        return redirect(url_for('service_list'))

    if form.button_save.data and form.validate():
        form.populate_obj(s)
        db.session.add(s)
        db.session.commit()
        if id == 0:
            db.session.flush()
            return redirect(url_for('edit_service', id=s.id))

    return render_template(
        'edit_service.html',
        service=s,
        form=form
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if db.session.query(User).count() == 0:
            u = User(user_login='admin', user_name='admin', user_password='admin')
            db.session.add(u)
            db.session.commit()
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
