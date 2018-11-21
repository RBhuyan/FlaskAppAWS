from flask import render_template, flash, redirect, url_for, request, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from application import app, db, bootstrap
from application.forms import LoginForm
from application.models import User, Menu
import io
import os
import csv
import zipfile
import shutil
import jinja2

#basedir = app.root_path
#HTMLfiles = '/HTMLfiles'
#UPLOAD_FOLDER = os.path.join(basedir, HTMLfiles)
#ALLOWED_EXTENSIONS = set(['.csv'])
UPLOAD_FOLDER = 'HTMLfiles/'
UPLOAD_FOLDER2 = 'HTMLfiles/MenuFiles/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])


@app.route('/')
@app.route('/index')
@login_required
def index():
    if (current_user.role == "teacher"):
        return redirect(url_for('teacher'))
    files = Menu.query.all()
    menuNames = []
    for file in files:
        totalName = "/HTMLfiles/" + file.filename
        menuNames.append(file)
        #menuNames.append(totalName)
    #files = db.session.query(Menu).query.all()
    if len(files) > 0:
        return render_template('index.html', title='Home', filenames=menuNames, bool='true')
    return render_template('index.html', title='Home')


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
            next_page = url_for('index')
        if user.role == "teacher":
            next_page = url_for('teacher')
        return redirect(next_page)
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
            flash("Database sucessfully created")
        return render_template('upload.html', users=listOfUsers)
    return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/teacher', methods=['GET', 'POST'])
@login_required
def teacher():
    if (current_user.role == "student"):
        return redirect(url_for('index'))
    if request.method == 'POST':
        file = request.files['ZippedHTML']
        if file.filename == '':
            print ("No such file exists")
            return redirect(url_for('teacher'))
        if file and allowed_file(file.filename):
            #First we want to clean the HTMLFiles and ZippedFile directories
            shutil.rmtree('ZippedFile/')
            shutil.rmtree('application/templates/HTMLfiles/')
            db.session.query(Menu).delete()
            os.makedirs('ZippedFile/')
            os.makedirs('application/templates/HTMLfiles/')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      #Saves the zip file into /HTMLfiles
            files_zip = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenameList = files_zip.namelist()
            for fName in filenameList:
                print(fName)
                menu = Menu(filename = fName)
                db.session.add(menu)
            db.session.commit()
            files_zip.extractall(app.config['UPLOAD_FOLDER2'])
            return render_template('teacher.html', bool='true') #Display the message that file transfer was successful
    return render_template('teacher.html')
