from flask import Flask , request, render_template, flash, redirect, url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

#CONFIGURATION DATABASE
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'patient_portal'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'      #default -> Returns Tuples, we want to use dictionary

#INIT DB
mysql = MySQL(app)

Articles = Articles()

#routes

@app.route('/')
def index(): 
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>')
def article(id):
    return render_template('article.html', id = id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min = 1, max = 50)])
    username = StringField('Username', [validators.Length(min = 4, max = 25)])
    email = StringField('Email', [validators.Length(min = 6, max = 50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Wrong passowrd')
    ])
    confirm = PasswordField('Confirm Password')

#REGISTRATION
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if(request.method == 'POST' and form.validate()):
        #   catching stuff
        name = form.name.data 
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #   cursor
        cur = mysql.connection.cursor()

        #   db command
        cur.execute("INSERT INTO patients(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #   commit 
        mysql.connection.commit()

        #   closing the connection
        cur.close()
        
        #  user message
        flash("Registered Successfully", 'success')

        redirect(url_for('index'))

    return render_template('register.html', form = form)






#APP    
if(__name__ == '__main__'):
    app.secret_key='secret123'
    app.run(debug = True)
