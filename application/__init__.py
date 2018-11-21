from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
import os

UPLOAD_FOLDER = 'ZippedFile/'
#UPLOAD_FOLDER2 = 'HTMLfiles/'
UPLOAD_FOLDER2 = 'application/templates/HTMLfiles/'
#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
#f.save(os.path.join(app.instance_path, 'csvDirectory', secure_filename(f.filename)))


from application import routes, models