from Project import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import validates


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

    userinfo = db.relationship('UserInfo', uselist=False, back_populates='user')

    def __repr__(self):
        user = "User('{username}', '{mail}', '{profile_picture}')".format(
            self.username, self.mail, self.profile_picture)
        return user

class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    night_mode = db.Column(db.Boolean, default=False)
    number_game_played =  db.Column(db.Integer, default=0)
    number_game_win =  db.Column(db.Integer, default=0)

    @validates('number_game_played', 'number_game_win')
    def fix_non_negative(self, key, value):
        if value < 0 or value is None:
            value = 0
        return value
        
    def check_log_invalides_values(self):
        errors = []

        if self.number_game_played < 0 or self.number_game_played is None:
            errors.append(f"number_game_played ne peut pas être inférieur à 0 ou none (valeur actuelle: {self.number_game_played})")
        if self.number_game_win < 0 or self.number_game_win is None:
            errors.append(f"number_game_win ne peut pas être inférieur à 0 ou none (valeur actuelle: {self.number_game_win})")

        return errors
    
    def save_user_infos(self):
        errors = self.check_log_invalides_values()

        if errors:
            print("Les erreurs suivantes ont été détecter et fix:")
            for error in errors:
                print(error)
        
        db.session.add(self)
        db.session.commit()

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User',back_populates='userinfo')