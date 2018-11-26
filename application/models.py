from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import db, login

'''
Creates the user table. ID is the primary key as each user has a unique id.

Usernames should also be unique as if we were to add further functionality in emailing for lost passwords we wouldn't know who to email if they only remember their username.

Role is either student or teacher, decided by the csv upload from the instructor

password_hash contains a hash of the passwork that is encrypted and decrypted by werkzeug.security (most popular security library for flask)

menuOne_fn, menuTwo_fn, and menuThree_fn are initialized to nulls and change to the filename of the menu that the user voted for in that position
This is useful because we can see if a user has voted or not by simply querying if these parameters are null or not
'''
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    menuOne_fn = db.Column(db.String(128), db.ForeignKey('menu.filename'))
    menuThree_fn = db.Column(db.String(128), db.ForeignKey('menu.filename'))
    menuTwo_fn = db.Column(db.String(128), db.ForeignKey('menu.filename'))

    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.role)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


'''
Pretty simple Menu table

ID is determined by what order the files are processed and are thus the primary key

Technically we could just have filename as a parameter, since because these are files in the same directory their filenames must be unique.

But indexing by ID is pretty standard for databases and doesn't have a significant memory or time cost so we chose to keep that parameter in.
'''
class Menu(db.Model):
    tablename = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(160))


    def __repr__(self):
        return '<Menu {}>'.format(self.filename)
