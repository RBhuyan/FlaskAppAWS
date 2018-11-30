from flask import render_template, flash, redirect, url_for, request, send_file, make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from application import app, db, bootstrap
from application.forms import LoginForm
from application.models import User
from flask_csv import send_csv
from flask_excel import init_excel
import io, os, csv, zipfile, shutil, random, fnmatch
from pathlib import PurePosixPath, PureWindowsPath, Path

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
    users = User.query.filter_by(role="student")
    userList = []
    for user in users:
        userList.append(user)
    if current_user.menuOne_fn is not None: #This means the first parameter for the user has been chosen
        return render_template('index.html', title='Home', alreadyVoted='true', firstPlace=current_user.menuOne_fn, secondPlace=current_user.menuTwo_fn, thirdPlace=current_user.menuThree_fn)

    #s = "/HTMLfiles/" + "u" + "/AmericanMenu.html"
    #fullFileNames.append(s)
    #s = "/HTMLfiles/" + "uu" + "/ChineseMenu.html"
    #fullFileNames.append(s)
    #s = "/HTMLfiles/" + "uuuu" + "/MexicanMenu.html"
    #fullFileNames.append(s)

    random.shuffle(userList)   #shuffles the order of the menus each time the page is loaded
    if users is None:
            return render_template('index.html', title='Home')
    firstMenu = request.args.get('firstMenu', '')
    secondMenu = request.args.get('secondMenu', '')
    thirdMenu = request.args.get('thirdMenu', '')
    if firstMenu == '' or secondMenu == '' or thirdMenu == '' or firstMenu == secondMenu or firstMenu == thirdMenu or secondMenu == thirdMenu : #Makes sure user selected a value in all dropdown boxes
        return render_template('index.html', title='Home', filenames=userList, bool='true')       #Also checks they are unique values.
    user = User.query.filter_by(username=firstMenu).first()
    current_user.menuOne_fn = user.username
    user = User.query.filter_by(username=secondMenu).first()
    current_user.menuTwo_fn = user.username
    user = User.query.filter_by(username=thirdMenu).first()
    current_user.menuThree_fn = user.username
    db.session.commit()
    return render_template('index.html', title='Home', filenames=userList, bool='true')



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
            user = User(username = "DEMO_TEACHER", role = "teacher")
            user.set_password("DEMO_PASSWORD")
            db.session.add(user)
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
            os.makedirs('ZippedFile/')
            os.makedirs('application/templates/HTMLfiles/')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))      #Saves the zip file into /HTMLfiles
            files_zip = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenameList = files_zip.namelist()
            pattern = "*.html"
            rootDir = "application/templates/HTMLfiles/"
            #We walk the root directory where menus are unzipped here
            files_zip.extractall(app.config['UPLOAD_FOLDER2'])

            #print(filenameList) #['u/AmericanMenu.html', 'uu/ChineseMenu.html', 'uuuu/MexicanMenu.html']
            for path in filenameList:
                print(Path(path).parts)
                pathParts = Path(path).parts
                user = User.query.filter_by(username=pathParts[0]).first()  # Directory names within zipped menus will be usernames
                user.filePath = "/HTMLfiles/" + user.username + "/" + pathParts[1]
            '''
            for dirName, subdirList, fileList in os.walk(rootDir):
                #print("DIRNAME: " + dirName)
                #print(dirName)
                #print("NEW LINE")
                #print(subdirList)
                #print(fileList)
                #print("END LINE")
                #for file in fileList:
                #    print("FILENAMES: " + file)
                user = User.query.filter_by(username=dirName).first() #Directory names within zipped menus will be usernames
                if user is not None:
                    for filename in fnmatch.filter(fileList, pattern): #We only want to get html files in the directory
                        user.filePath = filename    #Save the html filename as a property of the user in the database
            '''
            users = User.query.all()    #Query all users to refresh the filename property
            for user in users:
                user.menuOne_fn = None
                user.menuTwo_fn = None
                user.menuThree_fn = None
            db.session.commit()
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


#@app.errorhandler(404)
#def page_not_found(e):
#    return render_template('404.html'), 404