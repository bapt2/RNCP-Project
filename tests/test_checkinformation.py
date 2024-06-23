from Project import checkinformation, app, db
from Project.models import User
import pytest
import os


def test_Generate_Unique_Code():
    code = checkinformation.generateUniqueCode(12)
    assert len(code) == 12


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client


def test_Signin_Form_Invalide(client, monkeypatch):
    form_data = {
        'pseudo': 'exist_username',
        'mail': 'exist@test.com',
        'password': 'existpassword'
    }

    def mock_CheckUsername(username):
        return False

    def mock_CheckEmail(email):
        return False

    def mock_Password(password):
        return False

    monkeypatch.setattr('Project.checkinformation.checkUsername',
                        mock_CheckUsername)
    monkeypatch.setattr('Project.checkinformation.checkEmail',
                        mock_CheckEmail)
    monkeypatch.setattr('Project.checkinformation.checkPassword',
                        mock_Password)
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.post('/Inscription', data=form_data)
    assert response.status_code == 302, (
        'Ce nom d\'utilisateur existe déja veuillez en choisir un autre'
        in response.data.decode('utf-8'),
        'Ce email existe déja veuillez en choisir un autre'
        in response.data.decode('utf-8'))

    with client.session_transaction() as sess:
        sess.clear()


def test_Signin_Form_Valide(client, monkeypatch):
    form_data = {
        'pseudo': 'anotherusername',
        'email': 'another@test.com',
        'password': 'newpassword'
    }

    def mock_CheckUsername(username):
        return True

    def mock_CheckEmail(email):
        return True

    def mock_Password(password):
        return True

    monkeypatch.setattr('Project.checkinformation.checkUsername',
                        mock_CheckUsername)
    monkeypatch.setattr('Project.checkinformation.checkEmail',
                        mock_CheckEmail)
    monkeypatch.setattr('Project.checkinformation.checkPassword',
                        mock_Password)

    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.post('/Inscription', data=form_data,
                           follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as sess:
        sess.clear()

    user = User.query.filter_by(username='anotherusername').first()
    db.session.delete(user)
    db.session.commit()
