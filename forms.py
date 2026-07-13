from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from datetime import date

from models import User


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, message="Password minimal 6 karakter")]
    )
    confirm_password = PasswordField(
        "Konfirmasi Password",
        validators=[DataRequired(), EqualTo("password", message="Password tidak cocok")],
    )

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username sudah digunakan, pilih yang lain.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email sudah terdaftar.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class ExpenseForm(FlaskForm):
    amount = FloatField(
        "Jumlah (Rp)", validators=[DataRequired(), NumberRange(min=0.01, message="Jumlah harus lebih dari 0")]
    )
    category = SelectField("Kategori", validators=[DataRequired()])
    description = TextAreaField("Deskripsi", validators=[Length(max=255)])
    date = DateField("Tanggal", validators=[DataRequired()], default=date.today)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from flask import current_app
        self.category.choices = [(c, c) for c in current_app.config["CATEGORIES"]]
