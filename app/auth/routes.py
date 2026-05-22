from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required

from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User, Profile, Order

def get_auth_bp():
    from app.auth import auth_bp
    return auth_bp

@property
def auth_blueprint():
    return get_auth_bp()

# Альтернативный чистый синтаксис, чтобы обойти ошибку импорта:
from app.auth import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный email или пароль', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('auth.profile'))
        
    return render_template('auth/login.html', title='Личный кабинет B2B', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        
        profile = Profile(
            user_id=user.id,
            company_name=form.company_name.data,
            inn=form.inn.data,
            kpp=form.kpp.data,
            legal_address=form.legal_address.data
        )
        db.session.add(profile)
        db.session.commit()
        
        flash('Регистрация успешно завершена! Теперь вы можете войти на B2B-портал.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register_b2b.html', title='Регистрация дилера', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('auth/profile.html', title='Кабинет партнера', orders=orders)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))