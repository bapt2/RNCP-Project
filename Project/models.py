from Project import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_User(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    mail = db.Column(db.String(50), unique=True, nullable=False)
    profile_picture = db.Column(db.String(20), nullable=False,
                                default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        user = "User('{username}', '{mail}', '{profile_picture}')".format(
            self.username, self.mail, self.profile_picture)
        return user
