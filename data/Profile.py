from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional


class ProfileForm(FlaskForm):
    email = StringField("Почта", validators=[Optional()])
    password_new = PasswordField('Новый пароль', validators=[Optional()])
    telephone = StringField("Телефон", validators=[Optional()])
    img = StringField('Фотография', validators=[Optional()])
    password = PasswordField('Старый Пароль', validators=[Optional()])
    submit = SubmitField('Изменить')
