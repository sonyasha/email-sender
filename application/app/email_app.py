from flask import Flask, render_template, session, request, flash, jsonify, send_file, send_from_directory
from flask_pymongo import PyMongo
import datetime
import os
from flask_recaptcha import ReCaptcha
import smtplib
import time
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import io

MONGO_URL = os.environ.get('MONGODB_URI')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/email_app"

email_app = Flask(__name__)
email_app.secret_key = os.urandom(12)

site_key = os.environ.get('site_key')
secret_key = os.environ.get('secret_key')

email_app.config.update({'RECAPTCHA_ENABLED': True,
                   'RECAPTCHA_SITE_KEY': site_key,
                   'RECAPTCHA_SECRET_KEY': secret_key})

recaptcha = ReCaptcha(app=email_app)
email_app.config["MONGO_URI"] = MONGO_URL
mongo = PyMongo(email_app)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
gmail_username = None


@email_app.route('/')
def index():
    return render_template('index.html')

@email_app.route('/login', methods=['POST', 'GET'])
def do_login():

    if request.method == 'POST':
        session['logged_in'] = False
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
            return index()
        else:
            mongo.db.incorrect_logins.insert_one({'username': post_username, 'password': post_password, 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            flash('The username or password is incorrect.')
            flash('Please try again.')
            return index()
    
    else:
        session['logged_in'] = False
        session['gmail_logged'] = False
        return index()


@email_app.route('/logout')
def logout():
    session['logged_in'] = False
    session['gmail_logged'] = False
    return index()


@email_app.route('/gmail', methods=['POST', 'GET'])
def gmail():

    if request.method == 'POST':

        session['gmail_logged'] = False
        global server
        global gmail_username

        gmail_username = str(request.form['gmailname'])
        gmail_password = str(request.form['gmailpassword'])

        # if gmail_username and gmail_password and recaptcha.verify():
        if gmail_username and gmail_password:
            try: 
                server.login(gmail_username, gmail_password)
                session['gmail_logged'] = True
                # time.sleep(2)
                return index()
            except:
                flash('The email address or password is incorrect.')
                flash('Please try again.')
                return index()
        
        else:
            flash('The field is empty.')
            flash('Please try again.')
            return index()

    else:
        session['logged_in'] = False
        session['gmail_logged'] = False
        return index()


@email_app.route('/upload', methods=['POST', 'GET'])
def upload():

    if request.method == 'POST':
        # print(f'logged-in: {session["logged_in"]}')
        # print(f'gmail-in: {session["gmail_logged"]}')

        try:
            message_f = request.files['text']
            contacts_f = request.files['contacts']

            mes_content = message_f.read().decode("UTF8")
            message_template = Template(mes_content)
            
            stream = io.StringIO(contacts_f.stream.read().decode("UTF8"), newline=None)
            reader = csv.reader(stream)
            header = next(reader)
            contacts = [[line[0], line[1]] for line in reader]
            # print(f'contacts: {contacts}')
            
            for contact in contacts:
                name = contact[0]
                email = contact[1]
                print(name, email)

                message = MIMEMultipart()
                # print(f'message1: {message}')
                named_template = message_template.substitute(RECIPIENT_NAME=name.title())
                # print(f'named template: {named_template}')

                global gmail_username
                # print(gmail_username)
                message['From'] = gmail_username
                message['To'] = email
                message['Subject'] = "Test message"
                message.attach(MIMEText(named_template, 'plain'))
                # print(f'message2: {message}')

                server.send_message(message)
                # print(f'message3: {message}')

                del message
                mongo.db.contacts.insert_one({'name': name, 'email': email, 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            server.quit()

            session['logged_in'] = False
            session['gmail_logged'] = False
            flash('Your emails were successfully sent!')
            flash('Thank you for using this app')
            return index()

        except:
            flash('Files are not uploaded.')
            flash('Please try again.')
            return index()

    else:
        flash('Nothing was uploaded.')
        flash('Please try again.')
        return index()


@email_app.route('/download_contacts')
def download_cont():
    try:
        return send_file(os.path.abspath(os.getcwd()) + '/app/static/contacts_example.csv', as_attachment=True)
    except Exception as e:
	    return str(e)


@email_app.route('/download_message')
def download_mess():
    try:
	    return send_from_directory(os.path.abspath(os.getcwd()) + '/app/static', 'message_example.txt', as_attachment=True)
    except Exception as e:
	    return str(e)


if __name__ == "__main__":
    email_app.run(debug=True)