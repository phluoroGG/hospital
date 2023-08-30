from wtforms import StringField, SubmitField, IntegerField, DateField
from wtforms import validators
from wtforms_alchemy import ModelForm, QuerySelectField

from model import Department, Doctor, Patient, Service, RenderedService


class DepartmentForm(ModelForm):
    class Meta:
        model = Department

    name = StringField("Название отделения", validators=[
        validators.DataRequired(message="Название не может быть пустым"),
        validators.Length(min=3, max=50, message="Длина названия должна быть от 3 до 50 символов")])
    doctor = QuerySelectField("Заведующий отделением",
                              query_factory=lambda: Doctor.query.order_by(Doctor.id).all(),
                              get_pk=lambda d: d.id,
                              get_label=lambda d: d.name,
                              allow_blank=True)

    button_save = SubmitField("Сохранить")
    button_delete = SubmitField("Удалить")


class DoctorForm(ModelForm):
    class Meta:
        model = Doctor

    name = StringField("ФИО врача", validators=[
        validators.DataRequired(message="ФИО не может быть пустым"),
        validators.Length(min=3, max=50, message="ФИО должно быть от 3 до 50 символов")])
    department = QuerySelectField("Отделение",
                                  query_factory=lambda: Department.query.order_by(Department.id).all(),
                                  get_pk=lambda d: d.id,
                                  get_label=lambda d: d.name,
                                  allow_blank=True)
    salary = IntegerField("Зарплата врача", validators=[
        validators.DataRequired(message="Необходимо ввести размер зарплаты")])

    button_save = SubmitField("Сохранить")
    button_delete = SubmitField("Удалить")


class PatientForm(ModelForm):
    class Meta:
        model = Patient

    name = StringField("ФИО пациента", validators=[
        validators.DataRequired(message="ФИО не может быть пустым"),
        validators.Length(min=3, max=50, message="ФИО должно быть от 3 до 50 символов")])
    birthday = DateField("День рождения пациента")
    phone_number = StringField("Номер телефона пациента", validators=[
        validators.Length(min=3, max=15, message="Номер телефона должен быть от 3 до 15 символов")])

    button_save = SubmitField("Сохранить")
    button_delete = SubmitField("Удалить")


class PriceListForm(ModelForm):
    class Meta:
        model = Department

    name = StringField("Название услуги", validators=[
        validators.DataRequired(message="Название не может быть пустым"),
        validators.Length(min=3, max=50, message="Длина названия должна быть от 3 до 50 символов")])
    cost = IntegerField("Стоимость услуги", validators=[
        validators.DataRequired(message="Необходимо ввести стоимость услуги")])

    button_save = SubmitField("Сохранить")
    button_delete = SubmitField("Удалить")


class ServiceForm(ModelForm):
    class Meta:
        model = RenderedService

    patient = QuerySelectField("Пациент",
                               query_factory=lambda: Patient.query.order_by(Patient.id).all(),
                               get_pk=lambda p: p.id,
                               get_label=lambda p: p.name,
                               allow_blank=True)
    doctor = QuerySelectField("Доктор",
                              query_factory=lambda: Doctor.query.order_by(Doctor.id).all(),
                              get_pk=lambda d: d.id,
                              get_label=lambda d: d.name,
                              allow_blank=True)
    service = QuerySelectField("Услуга",
                               query_factory=lambda: Service.query.order_by(Service.id).all(),
                               get_pk=lambda s: s.id,
                               get_label=lambda s: s.name,
                               allow_blank=True)
    service_date = DateField("Дата проведения услуги")
    cost = IntegerField("Стоимость услуги", validators=[
        validators.DataRequired(message="Необходимо ввести стоимость услуги")])

    button_save = SubmitField("Сохранить")
    button_delete = SubmitField("Удалить")
