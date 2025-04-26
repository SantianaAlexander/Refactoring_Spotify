#IMPORT
from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.models import db, User
from flask_sqlalchemy import SQLAlchemy

auth_bp = Blueprint('auth', __name__)

#ENDPOINT REGISTER
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        email = request.form['email']
        if User.query.filter_by(username = username).first():
            return render_template('register.html', error="Questo username è già in uso. Ritenta!")
        new_user = User(username=username, password=hashed_password, email = email)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home.home'))
    return render_template('register.html', error=None)

#ENDPOINT LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home.home'))
        else:
            return render_template('login.html', error="Credenziali non valide.")
    return render_template('login.html', error=None)

#ENDPOINT LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))