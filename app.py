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

        return redirect(url_for('login'))

    return render_template('register.html', form = form)


# LOGIN

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        # GET FORM FIELDS
        username = request.form['username']
        # pass_can -> comparing the actual correct password from db
        passowrd_candidate = request.form['password']

        # CURSOR
        cur = mysql.connection.cursor()

        # GET PATIENT by username
        result = cur.execute("SELECT * FROM patients WHERE username = %s", [username])

        if(result > 0):
            # Acquiring stored hash
            data = cur.fetchone()       #gets the first one from the db response
            password = data['password']

            # Checking pass
            if(sha256_crypt.verify(passowrd_candidate, password)):
                app.logger.info('PASSWORD correct')         #May throw a false alarm 
            else:
                app.logger.info('PASSWORD incorrect')

    else:
        app.logger.info('Patient not found')       #May throw a false alarm      

    return render_template('login.html')    

#APP    
if(__name__ == '__main__'):
    app.secret_key='secret123'
    app.run(debug = True)
