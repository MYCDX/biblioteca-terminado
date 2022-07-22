
from time import strftime
from flask import Flask, request, session, redirect, url_for, render_template,flash
from flaskext.mysql import MySQL #importa archivos de mysql
from flask import send_from_directory
from datetime import datetime
from notifypy import Notify
import pymysql 
import re 
import os
from datetime import date
from datetime import datetime
import time
 

app = Flask(__name__)
 
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'cairocoders-ednalan'
app.secret_key="Develoteca"
 
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'testingdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

 
# http://localhost:5000/pythonlogin/ - this will be the login page
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM accountss WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
   
    # If account exists in accountss table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            #return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Nombre de usuario/contraseña incorrectos'
    
    return render_template('index.html', msg=msg)
 

# http://localhost:5000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # conecta
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
   
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM accountss WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'La cuenta ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Dirección de correo electrónico no válida!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de usuario debe contener solo caracteres y números!'
        elif not username or not password or not email:
            msg = 'Por favor rellena el formulario!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accountss table
            cursor.execute('INSERT INTO accountss VALUES (NULL, %s, %s, %s, %s)', (fullname, username, password, email)) 
            conn.commit() #almacena
   
            msg = 'Se ha registrado exitosamente!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Por favor rellena el formulario!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
  


# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
   
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
  
# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
 
# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile(): 
 # Check if account exists using MySQL
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accountss WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
  


@app.route('/crud')
def crud():
    sql = "SELECT * FROM  `accountss`;"
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)  
    accountss=cursor.fetchall() #selecciona registros
    print(accountss) #muestra registros
    conn.commit()
    return render_template('crud.html', accountss=accountss )



@app.route('/destroy/<int:id>')
def destroy(id):
    conn= mysql.connect()
    cursor=conn.cursor()    
    cursor.execute("DELETE FROM accountss WHERE id=%s",(id))
    conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM accountss WHERE id=%s",(id))   
    accountss=cursor.fetchall() #selecciona registros
    conn.commit() 
    return render_template('edit.html',accountss=accountss)
 

@app.route('/update', methods=['POST'])
def update():

    fullname=request.form['txtNombre']
    username=request.form['txtUsername']
    password=request.form['txtContraseña']
    email=request.form['txtCorreo']    
    id=request.form['txtID']
    sql ="UPDATE accountss SET fullname=%s, username=%s, password=%s, email=%s WHERE  id=%s ;"

    datos=(fullname,username,password,email,id)  
    conn= mysql.connect()
    cursor=conn.cursor()

    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/store', methods=['POST'])
def storage():
    fullname=request.form['txtNombre']
    username=request.form['txtUsername']
    password=request.form['txtContraseña']
    email=request.form['txtCorreo']
  
    sql = "INSERT INTO `accountss` (`id`, `fullname`, `username`, `password`,`email`) VALUES (NULL, %s, %s, %s, %s);"
    
    datos=(fullname,username,password,email)
    
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')



# http://localhost:5000/register - this will be the registration page

@app.route('/libros', methods=['GET', 'POST'])
def libros():
    # conecta
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'libro' in request.form and 'fecha' in request.form:
        # Create variables for easy acces

        libro = request.form['libro']
        fecha = request.form['fecha']
        
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM lib WHERE libro = %s', (libro))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if not libro:
            msg = 'Por favor rellena el formulario!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accountss table
            cursor.execute('INSERT INTO lib VALUES (NULL, %s, %s)', (libro, fecha)) 
            conn.commit() #almacena
   
            msg = 'Se ha registrado exitosamente!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Por favor rellena el formulario!'
    # Show registration form with message (if any)
    return render_template('libros.html', msg=msg)
  

@app.route('/crud_libro')
def crud_libro():
    
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accountss WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        
        
        sql = "SELECT * FROM  `lib`;"
        conn= mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql)  
        lib=cursor.fetchall() #selecciona registros
        print(lib) #muestra registros
        conn.commit()
        return render_template('crud_libro.html', lib=lib, account = account )

@app.route('/crud_lib')
def crud_lib():
    sql = "SELECT * FROM  `lib`;"
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)  
    lib=cursor.fetchall() #selecciona registros
    print(lib) #muestra registros
    conn.commit()
    return render_template('crud_lib.html', lib=lib )


@app.route('/destroy_1/<int:id_libro>')
def destroy_1(id_libro):
    conn= mysql.connect()
    cursor=conn.cursor()    
    cursor.execute("DELETE FROM lib WHERE id_libro=%s",(id_libro))
    conn.commit()
    return render_template('libros.html')

@app.route('/create_libro')
def create_libro():
    return render_template('libros.html')

# imprimimos la constancia de prestamo 
@app.route('/imprimir')
def imprimir():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accountss WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        
        
        sql = "SELECT * FROM  `lib`;"
        conn= mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql)  
        lib=cursor.fetchall() #selecciona registros
        print(lib) #muestra registros
        conn.commit()
        return render_template('imprimir.html', lib=lib, account = account )


# imprimimos la lsita de libros
@app.route('/imprimir_lista')
def imprimir_lista():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accountss WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        
        
        sql = "SELECT * FROM  `libros`;"
        conn= mysql.connect()
        cursor=conn.cursor()
        cursor.execute(sql)  
        libros=cursor.fetchall() #selecciona registros
        print(libros) #muestra registros
        conn.commit()
        return render_template('imprimir_lista.html', libros=libros, account = account )

if __name__ == '__main__':
    app.run(debug=True)

