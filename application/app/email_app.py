from flask import Flask, render_template, session, request, flash
from flask_pymongo import PyMongo
import os

email_app = Flask(__name__)
mongo = PyMongo(email_app)

@email_app.route('/')
def index():

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@email_app.route('/login', methods=['POST'])
def do_login():

    if request.method == 'POST':
        post_username = str(request.form['username'])
        post_password = str(request.form['password'])

        credentials = mongo.db.users.find()
        right_user = False

        for u in credentials:
            if post_username == u['username'] and post_password == u['password']:
                right_user = True
                break
            else:
                right_user = False

        if right_user:
            session['logged_in'] = True
        else:
            flash('The username or password is incorrect.')
            flash('Please try again.')
        return index()

@email_app.route('/logout')
def logout():
    session['logged_in'] = False
    return index()

if __name__ == "__main__":
    email_app.secret_key = os.urandom(12)
    email_app.run(debug=True)