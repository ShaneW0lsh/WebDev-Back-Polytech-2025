from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from lab1.app import app as lab1_app
from lab2.app import app as lab2_app
from lab3.app import app as lab3_app
from lab4.app import app as lab4_app, init_db as init_lab4_db
from lab5.app import app as lab5_app, init_db as init_lab5_db
from root_app.app import app as root_app

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(root_app, {
    '/lab1': lab1_app,
    '/lab2': lab2_app,
    '/lab3': lab3_app,
    '/lab4': lab4_app,
    '/lab5': lab5_app
})

init_lab4_db()
init_lab5_db()

application = app

if __name__ == "__main__":
    app.run();