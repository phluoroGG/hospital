from app_config import db


class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column('id', db.INTEGER, primary_key=True, autoincrement=True)
    head = db.Column(db.ForeignKey('doctor.id', onupdate='SET NULL', ondelete='CASCADE'), unique=True)
    name = db.Column('name', db.String(50), nullable=False)
    doctor = db.relationship('Doctor', foreign_keys=[head])


class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column('id', db.INTEGER, primary_key=True, autoincrement=True)
    department_id = db.Column(db.ForeignKey('department.id', onupdate='SET NULL', ondelete='CASCADE'))
    name = db.Column('name', db.String(50), nullable=False)
    salary = db.Column('salary', db.INTEGER, nullable=False)
    department = db.relationship('Department', foreign_keys=[department_id])


class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column('id', db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50), nullable=False)
    birthday = db.Column('birthday', db.DATE)
    phone_number = db.Column('phone_number', db.String(20))


class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column('id', db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50), nullable=False)
    cost = db.Column('cost', db.INTEGER, nullable=False)


class RenderedService(db.Model):
    __tablename__ = 'rendered_service'
    id = db.Column('id', db.INTEGER, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.ForeignKey('patient.id', onupdate='SET NULL', ondelete='CASCADE'))
    doctor_id = db.Column(db.ForeignKey('doctor.id', onupdate='SET NULL', ondelete='CASCADE'))
    service_id = db.Column(db.ForeignKey('service.id', onupdate='SET NULL', ondelete='CASCADE'))
    service_date = db.Column('service_date', db.DATE, nullable=False)
    cost = db.Column('cost', db.INTEGER, nullable=False)
    patient = db.relationship('Patient')
    doctor = db.relationship('Doctor')
    service = db.relationship('Service')


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column('user_id', db.INTEGER, primary_key=True, autoincrement=True)
    user_login = db.Column('user_login', db.String(20), unique=True)
    user_name = db.Column('user_name', db.String(60), nullable=False)
    user_password = db.Column('user_password', db.String(60), nullable=False)

    # Flask-Login Support
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return str(self.user_id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
