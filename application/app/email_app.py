from flask import Flask, render_template, session, request, flash
from flask_pymongo import PyMongo
import datetime
import os
from flask_recaptcha import ReCaptcha
from keys import site_key, secret_key

# MONGO_URL = os.environ.get('MONGODB_URI')
# if not MONGO_URL:
#     MONGO_URL = "mongodb://localhost:27017/email_app"

email_app = Flask(__name__)

email_app.config.update({'RECAPTCHA_ENABLED': True,
                   'RECAPTCHA_SITE_KEY': site_key,
                   'RECAPTCHA_SECRET_KEY': secret_key})

recaptcha = ReCaptcha(app=email_app)
# email_app.config["MONGO_URI"] = MONGO_URL
mongo = PyMongo(email_app)


@email_app.route('/')
def index():

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@email_app.route('/login', methods=['POST', 'GET'])
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

        if right_user and recaptcha.verify():
            session['logged_in'] = True
        else:
            mongo.db.incorrect_logins.insert_one({'username': post_username, 'password': post_password, 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            flash('The username or password is incorrect.')
            flash('Please try again.')
        return index()
    
    if request.method == 'GET':
        session['logged_in'] = False
        return index()


@email_app.route('/logout')
def logout():
    session['logged_in'] = False
    return index()


@email_app.route('/gmail', methods=['POST', 'GET'])
def gmail():

    if request.method == 'POST':

        import smtplib
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        gmail_username = str(request.form['gmailname'])
        gmail_password = str(request.form['gmailpassword'])

        if gmail_username and gmail_password and recaptcha.verify():
            try:
                server.login(gmail_username, gmail_password)
                print('logged in')
                return 'logged in'
            except:
                flash('The username or password is incorrect.')
                flash('Please try again.')
                return index()

    if request.method == 'GET':
        session['logged_in'] = False
        return index()


if __name__ == "__main__":
    email_app.secret_key = os.urandom(12)
    email_app.run(debug=True)