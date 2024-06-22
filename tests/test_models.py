from Project import app, db
import pytest
import os
from Project.models import User


@pytest.fixture(scope='module')
def test_Client():
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def initDataBase(test_Client):
    db.create_all()

    user1 = User(username='testuser1', mail='test1@exemple.com',
                 password='password1')
    user2 = User(username='testuser2', mail='test2@exemple.com',
                 password='password2')
    db.session.add(user1)
    db.session.add(user2)

    db.session.commit()

    yield db

    db.session.delete(user1)
    db.session.delete(user2)

    db.session.commit()


def test_User_Model(initDataBase):
    user = User.query.filter_by(username='testuser1').first()
    assert user is not None
    assert user.id is not None
    assert user.username == 'testuser1'
    assert user.mail == 'test1@exemple.com'
    assert user.password == 'password1'
    assert user.profile_picture == 'default.jpg'


def test_User_Creation(initDataBase):
    new_user = User(username='newuser',
                    mail='newuser@exemple.com',
                    password='newpassword')
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.id is not None
    assert user.username == 'newuser'
    assert user.mail == 'newuser@exemple.com'
    assert user.password == 'newpassword'
    assert user.profile_picture == 'default.jpg'

    db.session.delete(new_user)

    db.session.commit()


def test_User_Id_Unique(initDataBase):
    user1 = User.query.filter_by(username='testuser1').first()
    user2 = User.query.filter_by(username='testuser2').first()
    assert user1.id != user2.id


def test_User_Username_Unique(initDataBase):
    user1 = User.query.filter_by(username='testuser1').first()
    user2 = User.query.filter_by(username='testuser2').first()
    assert user1.username != user2.username


def test_User_Mail_Unique(initDataBase):
    user1 = User.query.filter_by(mail='test1@exemple.com').first()
    user2 = User.query.filter_by(mail='test2@exemple.com').first()
    assert user1.mail != user2.mail
