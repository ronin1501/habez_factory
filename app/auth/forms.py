from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User, Profile

class LoginForm(FlaskForm):
    """Форма авторизации на B2B-портале"""
    email = StringField('Email организации', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти в систему')

class RegistrationForm(FlaskForm):
    """Форма регистрации нового дилера (Юр. лица)"""
    email = StringField('Email организации', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Контактный телефон', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, message='Пароль должен быть не менее 6 знаков')])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    
    # B2B Поля компании
    company_name = StringField('Название компании / ИП', validators=[DataRequired(), Length(max=200)])
    inn = StringField('ИНН компании', validators=[DataRequired(), Length(min=10, max=12, message='ИНН должен содержать 10 или 12 цифр')])
    kpp = StringField('КПП (для ИП введите 0)', validators=[DataRequired(), Length(min=1, max=9)])
    legal_address = StringField('Юридический адрес', validators=[DataRequired()])
    
    submit = SubmitField('Подать заявку на дилерство')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Данный Email уже зарегистрирован в системе.')

    def validate_inn(self, inn):
        profile = Profile.query.filter_by(inn=inn.data).first()
        if profile:
            raise ValidationError('Компания с таким ИНН уже подавала заявку.')