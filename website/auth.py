from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


#blueprint for all authentication pages
auth = Blueprint('auth', __name__)

#login
@auth.route('/login', methods=["GET","POST"])
def login():
    logout_user()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #find user
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                #if passwords match, user logs in successfully
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session['user']=user.id #adds user to session
                return redirect(url_for('views.welcome'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    #in case of failed login
    return render_template("login.html", user=current_user)

#delete later
@auth.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

#logout
@auth.route('logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None) #removes user from current session
    return redirect(url_for('auth.login'))

#sign up
@auth.route('sign-up', methods=["GET","POST"])
def sign_up():
    logout_user()
    if request.method == 'POST':
        #gets all info
        email = request.form.get('email')
        username = request.form.get('username')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        #tries to find existing user with the same email
        user = User.query.filter_by(email=email).first()
        user1 = User.query.filter_by(username=username).first()
        if user:
            flash('Email already exists!', category='error')
        elif user1:
            flash('Username already exists!', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(username) < 1:
            flash('Enter username.', category='error')
        elif len(first_name) < 2:
            flash('First name must be at least 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            #add new user to database
            new_user = User(email=email, username=username, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            #logs in new user
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.welcome'))

    return render_template('sign_up.html', user=current_user)