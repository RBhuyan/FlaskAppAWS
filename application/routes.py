from flask import render_template, flash, redirect, url_for, request, send_file, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from application import app, db, bootstrap
from application.forms import LoginForm
from application.models import User, Menu
from flask_csv import send_csv
from flask_excel import init_excel
import io, os, csv, zipfile, shutil, random

#basedir = app.root_path
#HTMLfiles = '/HTMLfiles'
#UPLOAD_FOLDER = os.path.join(basedir, HTMLfiles)
#ALLOWED_EXTENSIONS = set(['.csv'])
UPLOAD_FOLDER = 'HTMLfiles/'
UPLOAD_FOLDER2 = 'HTMLfiles/MenuFiles/'
ALLOWED_EXTENSIONS = set(['zip'])


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if (current_user.role == "teacher"):
        return redirect(url_for('teacher')) #If a teacher somehow gets to this student page we redirect them to teacher page
    files = Menu.query.all()
    #files = User.query.all()
    menuNames = []
    if current_user.menuOne_fn is not None: #This means not even the first parameter for the user has been chosen
        return render_template('index.html', title='Home', alreadyVoted='true', firstPlace=current_user.menuOne_fn, secondPlace=current_user.menuTwo_fn, thirdPlace=current_user.menuThree_fn)
    for file in files:
        menuNames.append(file)
    random.shuffle(menuNames)   #shuffles the order of the menus each time the page is loaded
    if len(files) <= 0:
            return render_template('index.html', title='Home')
    firstMenu = request.args.get('firstMenu', '')
    secondMenu = request.args.get('secondMenu', '')
    thirdMenu = request.args.get('thirdMenu', '')
    if firstMenu == '' or secondMenu == '' or thirdMenu == '' or firstMenu == secondMenu or firstMenu == thirdMenu or secondMenu == thirdMenu : #Makes sure user selected a value in all dropdown boxes
        return render_template('index.html', title='Home', filenames=menuNames, bool='true')       #Also checks they are unique values.
    menu = Menu.query.filter_by(filename=firstMenu).first()
    current_user.menuOne_fn = menu.filename
    menu = Menu.query.filter_by(filename=secondMenu).first()
    current_user.menuTwo_fn = menu.filename
    menu = Menu.query.filter_by(filename=thirdMenu).first()
    current_user.menuThree_fn = menu.filename
    db.session.commit()
    return render_template('index.html', title='Home', filenames=menuNames, bool='true')



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
                print(fName)    #DEBUGGING PURPOSES
                menu = Menu(filename = fName)
                db.session.add(menu)
            users = User.query.all()
            for user in users:
                user.menuOne_fn = None
                user.menuTwo_fn = None
                user.menuThree_fn = None
            db.session.commit()
            files_zip.extractall(app.config['UPLOAD_FOLDER2'])
            return render_template('teacher.html', bool='true') #Display the message that file transfer was successful
    return render_template('teacher.html')


@app.route('/teacherReport', methods=['GET', 'POST'])
def teacherReport():
    users = User.query.all()    #returns a list of all users
    return render_template('teacherReport.html')

@app.route('/download', methods=['GET', 'POST'])    #Function called by the button in the download excel page
def download():
    users = User.query.all()
    tempDicEntry = ["USERNAME", "VOTE 1", "VOTE 2", "VOTE 3"]
    csv = 'USERNAME,VOTE 1,VOTE 2,VOTE3\n'
    for user in users:
        if user.menuOne_fn is None:
            user.menuOne_fn = ''
            user.menuTwo_fn = ''
            user.menuThree_fn = ''
        tempString = user.username + ',' + user.menuOne_fn + ',' + user.menuTwo_fn + ',' + user.menuThree_fn + '\n'
        csv += tempString
    for user in users:
        if user.menuOne_fn == '':
            user.menuOne_fn = None
            user.menuTwo_fn = None
            user.menuThree_fn = None
    response = make_response(csv)
    cd = 'attachment; filename=studentVotingReports.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response


@app.route('/studentReport')
def studentReport():
    return render_template('studentReport.html')