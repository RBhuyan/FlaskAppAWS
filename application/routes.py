from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from application import app, db
from application.forms import LoginForm
from application.models import User
import io
import os
import csv

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, '/csvUpload')
ALLOWED_EXTENSIONS = set(['.csv'])


@app.route('/')
@app.route('/index')
@login_required
def index():
    menus = [
        {
            'body': 'Filename 1'
        },
        {
            'body': 'Filename 2'
        }
    ]
    return render_template('index.html', title='Home', posts=menus)

@app.route('/teacher')
@login_required
def teacher():
    return render_template('teacher.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        #if not next_page or url_parse(next_page).netloc != '':
        if user.role == "student":
            print("THINKS IT'S A STUDENT")
            next_page = url_for('index')
        if user.role == "teacher":
            print("THINKS IT'S A TEACHER")
            next_page = url_for('teacher')
        print("FAILED LAST IF CONDITION")
        return redirect(next_page)
    print("FORM DID NOT VALIDATE")
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if not f:
            flash ("No file")
            return redirect(url_for('upload.html'))
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        listOfUsers = []
        for row in csv_input:
            user = User(username = row[0].strip(), role = row[2].strip())
            user.set_password(row[1].strip())
            listOfUsers.append(user)
        if len(listOfUsers) > 0:
            db.session.query(User).delete()
            for u in listOfUsers:
                db.session.add(u)
            db.session.commit()
        return render_template('upload.html', users=listOfUsers)
    return render_template('upload.html')



'''
@app.route('/register', methods=['GET', 'POST'])
def register():
        user = User(username=form.username.data, role=form.roleType.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
'''