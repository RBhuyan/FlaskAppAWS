from application import app, db
from application.models import User, Menu
from flask import Flask

import sys
import os
#sys.path.append("/opt/python/current/app/FlaskAppAWS")

application = Flask(__name__)
application = app


@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Menu': Menu}

if __name__ == "__main__":
    app.run()