from flask import Flask, render_template, session, request, flash, jsonify
from flask_pymongo import PyMongo
import datetime
import os
from flask_recaptcha import ReCaptcha
# from keys import site_key, secret_key
import smtplib

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
    print(session['logged_in'])
    print(session['gmail_logged'])

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

        if gmail_username and gmail_password and recaptcha.verify():
            
            try: 
                server.login(gmail_username, gmail_password)
                session['gmail_logged'] = True
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


@email_app.route('/upload', methods=['POST'])
def upload():

    if request.method == 'POST':

        try:
            message_f = request.files['text']
            contacts_f = request.files['contacts']

            from string import Template
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import csv
            import io

            mes_content = message_f.read().decode("UTF8")
            message_template = Template(mes_content)

            stream = io.StringIO(contacts_f.stream.read().decode("UTF8"), newline=None)
            reader = csv.reader(stream)
            header = next(reader)
            contacts = [[line[0], line[1]] for line in reader]
            
            for contact in contacts:
                name = contact[0]
                email = contact[1]

                message = MIMEMultipart()
                named_template = message_template.substitute(RECIPIENT_NAME=name.title())

                message['From'] = gmail_username
                message['To'] = email
                message['Subject'] = "Test message"
                message.attach(MIMEText(named_template, 'plain'))

                server.send_message(message)
                print(message)

                del message
                mongo.db.contacts.insert_one({'name': name, 'email': email, 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            server.quit()

            session['logged_in'] = False
            session['gmail_logged'] = False
            flash('Your emals were successfully sent')
            flash('Thank you for using this app')
            return index()

        except:
            flash('Files are not uploaded.')
            flash('Please try again.')
            return index()


if __name__ == "__main__":
    email_app.run(debug=True)