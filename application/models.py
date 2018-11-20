from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import db, login

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    menuOne_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    menuThree_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    menuTwo_id = db.Column(db.Integer, db.ForeignKey('menu.id'))

    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.role)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Menu(db.Model):
    tablename = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(160))


    def __repr__(self):
        return '<Menu {}>'.format(self.body)
