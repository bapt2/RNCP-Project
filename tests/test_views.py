from flask_login import FlaskLoginClient
from Project import app
import pytest
import os


app.test_client_class = FlaskLoginClient

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_Home(client):
    response = client.get('/')
    assert response.status_code == 200
    response = client.get('/Accueil')
    assert response.status_code == 200

def test_Info(client):
    response = client.get('/Information')
    assert response.status_code == 200


def test_Type(client):
    response = client.get('/Type')
    assert response.status_code == 200


def test_Signin(client):
    response = client.get('/Inscription')
    assert response.status_code == 200


def test_Login(client):
    response = client.get('/Connexion')
    assert response.status_code == 200


def test_Logout(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    response = client.get('/Deconnexion', follow_redirects=True)
    assert response.status_code == 200


def test_Account(client): 
    response = client.post('Connexion', json={'username': 'testuser'}, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/Compte', follow_redirects=True)
    assert response.status_code == 200
