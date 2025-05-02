import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client
 

def test_counter(client):
    res1 = client.get('/counter')
    assert 'Вы посетили данную таблицу 1 раз!'.encode('utf-8') in res1.data
    
    res2 = client.get('/counter')
    assert 'Вы посетили данную таблицу 2 раз!'.encode('utf-8') in res2.data

def test_successful_login(client):
    response = client.post('/login', data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)    
    assert 'Вы успешно авторизованы'.encode('utf-8') in response.data

def test_unsuccessful_login(client):
    response = client.post('/login', data={'username': 'user', 'password': 'wrong'}, follow_redirects=True)
    assert 'Пользователь не найден'.encode('utf-8') in response.data

def test_authenticated_user_access_secret(client):
    client.post('/login', data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)
    response = client.get('/secret')
    assert 'Вы попали на страницу для залогированных пользователей'.encode('utf-8') in response.data

def test_anonymous_user_redirected_from_secret(client):
    response = client.get('/secret', follow_redirects=True)
    assert 'Для доступа к данной странице нужно аутентифицироваться'.encode('utf-8') in response.data

def test_redirect_after_login(client):
    response = client.get('/secret', follow_redirects=False)
    assert response.status_code == 302
    login_url = response.headers['Location']
    response = client.post(login_url, data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)
    assert 'Вы попали на страницу для залогированных пользователей'.encode('utf-8') in response.data

def test_remember_me(client):
    response = client.post('/login', data={'username': 'user', 'password': 'qwerty', 'remember_me': 'on'})
    assert 'remember_token' in response.headers.get('Set-Cookie', '')

def test_navbar_authenticated(client):
    client.post('/login', data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)
    response = client.get('/')
    assert 'Секрет'.encode('utf-8') in response.data
    assert 'Выйти'.encode('utf-8') in response.data
    assert 'Войти'.encode('utf-8') not in response.data

def test_navbar_anonymous(client):
    response = client.get('/')
    assert 'Секрет'.encode('utf-8') not in response.data
    assert 'Выйти'.encode('utf-8') not in response.data
    assert 'Войти'.encode('utf-8') in response.data

def test_logout(client):
    client.post('/login', data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы вышли из системы'.encode('utf-8') in response.data 