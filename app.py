from flask import Flask , request, render_template, flash, redirect, url_for, session, logging
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)

#CONFIGURATION DATABASE
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'patient_portal'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'      #default -> Returns Tuples, we want to use dictionary

#INIT DB
mysql = MySQL(app)

#Articles = Articles()

#routes

# Home
@app.route('/')
def index(): 
    return render_template('home.html')

# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

#Articles
@app.route('/articles')
def articles():
    return render_template('articles.html', articles = articles)

#Single article
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
               # app.logger.info('PASSWORD correct')         #May throw a false alarm 
               session['logged_in'] = True
               session['username'] = username

               flash('Welcome back', 'success')
               return redirect(url_for('dashboard'))

            else:
                errorMsg = 'Oops recheck your password'
                return render_template('login.html', error=errorMsg)
            
            # closing the connection
            cur.close()
        else:
            errorMsg = 'username not found'
            return render_template('login.html', error=errorMsg)

    return render_template('login.html')    

# Check logIns
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwrags):
        if('logged_in' in session):
            return f(*args, **kwrags)
        else:
            flash('Maybe try logging in first?', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logging out
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logged out', 'success')
    return redirect(url_for('login'))


# DASHBOARD
@app.route('/dashboard')
@is_logged_in
def dashboard():

    #   Create cursor
    cur = mysql.connection.cursor()

    # GET stuff
    result = cur.execute("SELECT * FROM medical_data")

    # Fetching in dictionary form
    articles = cur.fetchall()

    if(result > 0):
        return render_template('dashboard.html', articles = articles)
        
    else:
        msg = "No medical data found"
        return render_template('dashboard.html', msg = msg)
        
    
    #close connec
    cur.close()

class PatientDataForm(Form):
    doctor = StringField('Doctor', [validators.Length(min = 1, max = 50)])
    diagnosis = TextAreaField('Diagnosis', [validators.Length(min = 10)])


# ADDING PATIENT DATA
@app.route('/add_patient_data', methods= ['GET', 'POST'])
@is_logged_in
def add_patient_data():
    form = PatientDataForm(request.form)
    if(request.method == 'POST' and form.validate()):
        doctor = form.doctor.data
        diagnosis = form.diagnosis.data 

        #CREATE CURSOR
        cur = mysql.connection.cursor()

        #Excecute
        cur.execute("INSERT INTO medical_data(doctor, diagnosis, patient) VALUES(%s, %s, %s)", (doctor, diagnosis, session['username']))

        #COMMIT
        mysql.connection.commit()

        #CLOSE 

        cur.close()

        flash("Data successfully entered", "success")

        return redirect(url_for('dashboard'))
    
    return render_template('add_patient_data.html', form = form)

# EDIT patient data
@app.route('/edit_patient_data/<string:id>', methods= ['GET', 'POST'])
@is_logged_in
def edit_patient_data(id):
    #Create cursor
    cur = mysql.connection.cursor()
    
    #Get the patient_data by ID
    result = cur.execute("SELECT * FROM medical_data WHERE id = %s", [id])

    article = cur.fetchone()

    # GET form
    form = PatientDataForm(request.form)

    # Editing the data feilds
    form.doctor.data = article['doctor']
    form.diagnosis.data = article['diagnosis']

    form = PatientDataForm(request.form)
    if(request.method == 'POST' and form.validate()):
        doctor = form.doctor.data
        diagnosis = form.diagnosis.data 

        #CREATE CURSOR
        cur = mysql.connection.cursor()
        #cur.execute("UPDATE medical_data(doctor, diagnosis, patient) VALUES(%s, %s, %s)", (doctor, diagnosis, session['username']))

        #Excecute
        cur.execute("UPDATE medical_data SET doctor = %s, diagnosis = %s WHERE id = %s", (doctor, diagnosis,id))

        #COMMIT
        mysql.connection.commit()

        #CLOSE 

        cur.close()

        flash("Data successfully entered", "success")

        return redirect(url_for('dashboard'))
    
    return render_template('edit_patient_data.html', form = form)

#APP    
if(__name__ == '__main__'):
    app.secret_key='secret123'
    app.run(debug = True)

#END