# pip install flask 
# pip install Flask-SQLAlchemy flask_login flask_bcrypt flask_wtf wtforms email_validator 
# from distutils.command.upload import upload
import sqlite3
from flask import Flask,make_response,url_for,redirect, request, render_template,current_app, g, send_file,flash
from flask_sqlalchemy import SQLAlchemy
#login 
from flask_login import UserMixin, LoginManager,login_user,login_required,logout_user,current_user
#form 
from flask_wtf import FlaskForm
from sqlalchemy import false # mistake (wtforms)
from wtforms import StringField,PasswordField, SubmitField
from wtforms.validators import InputRequired,Length,ValidationError
from flask_bcrypt import Bcrypt
##from flask_bootstrap import Bootstrap
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from identify import getImplantType
import numpy as np
app = Flask(__name__)
app.config['SECRET_KEY']='rahaf'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
databasename = '_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + databasename
userstablename = "user" 
images_table_name = "upload" 
############## login manager #########
login_manager = LoginManager()    # pip install flask-login 
login_manager.init_app(app) 
login_manager.login_view ="login"

<<<<<<< HEAD

=======
############################
>>>>>>> 5856d3075e43bfe894ee3457921b9d527207c4f3
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

########## DB CLASS ###########
class User(db.Model,UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20),nullable = False,unique = True)
  email = db.Column(db.String(40),nullable = False,unique = True)
  password = db.Column(db.String(80),nullable = False)

class Upload(db.Model,UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  imagename = db.Column(db.String(80),nullable = False,unique = True)
  doctoremail = db.Column(db.String(80),nullable = False,)
  patientname = db.Column(db.String(20),nullable = False)
  patientemail = db.Column(db.String(40),nullable = False)
  comment = db.Column(db.String(40))
  topman = db.Column(db.String(40))
  manufacturer = db.Column(db.String(40))
  bw_lvl = db.Column(db.Integer())

########## FLASK FORM  ###########
class RegisterForm(FlaskForm):
  username2 = StringField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Username"})
  email2 = StringField(validators = [InputRequired(),Length(min=4,max=40)],render_kw={"placeholder":"Email"})
  password2 = PasswordField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})
  submit = SubmitField("Register")

  def validate_username(self, username):
    existing_user_username = User.query.filter_by(username=username.data).first()

    if existing_user_username:
      raise ValidationError("That user name already exists")
  
  def validate_email(self, email):
    existing_email_email = User.query.filter_by(email=email.data).first()

    if existing_email_email:
      raise ValidationError("That email name already exists")


class LoginForm(FlaskForm):
  email1 = StringField(validators = [InputRequired(),Length(min=4,max=40)],render_kw={"placeholder":"Email"})
  password1 = PasswordField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})
  submit = SubmitField("Login")

class UploadForm(FlaskForm):
  patientname = StringField(validators = [InputRequired(),Length(min=2,max=20)],render_kw={"placeholder":"Name"})
  patientemail = StringField(validators = [InputRequired(),Length(min=4,max=40)],render_kw={"placeholder":"Email"})
  comment = StringField(validators = [InputRequired(),Length(min=0,max=40)],render_kw={"placeholder":"Comment"})
  bw_lvl = StringField(validators = [InputRequired(),Length(min=0,max=3)],render_kw={"placeholder":"BW LVL"})

  submit = SubmitField("Upload")

##################################
try:
  print(f'Checking if {databasename} exists or not...')
  conn = sqlite3.connect(databasename, uri=True)
  print(f'Database exists. Succesfully connected to {databasename}')
  conn.execute('CREATE TABLE IF NOT EXISTS ' + userstablename + ' (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL, states INTEGER)')
  conn.execute('CREATE TABLE IF NOT EXISTS ' + images_table_name + ' (id INTEGER PRIMARY KEY AUTOINCREMENT,doctoremail TEXT NOT NULL,patientemail TEXT,patientname TEXT,imagename TEXT NOT NULL,topman TEXT NOT NULL,bw_lvl INTEGER,manufacturer TEXT,comment TEXT)')
  
  print(f'Succesfully Created Table {userstablename}')
  
  conn.close()

except sqlite3.OperationalError as err:
  print('Database does not exist')
  print(err)


####### route ###### 
@app.route('/') 
def index():
    return render_template('index.html')


@app.route('/login',methods=['GET','POST'])
def login():
  message = ""
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))

  form1 = LoginForm()
  form2 = RegisterForm()

  if request.method == "POST":

    if form1.validate_on_submit():
      # Login and validate the user.
      # user should be an instance of `User` class
      user = User.query.filter_by(email=form1.email1.data).first()      
     
      if user:
       
        if bcrypt.check_password_hash(user.password, form1.password1.data):
          login_user(user)
          return redirect(url_for('dashboard'))
        
        else:
          message = " !!!!!! Invalid username or password !!!!!"

      else:
        message = " !!!!!! Invalid username or password !!!!!"
        
  if request.method == "POST":
    if form2.validate_on_submit():
      hashed_password = bcrypt.generate_password_hash(form2.password2.data)
      user = User.query.filter_by(email=form2.email2.data).first() 
      if user:
        message = " the email is already registered "
      elif User.query.filter_by(username=form2.username2.data).first():
        message =" the username is already registered "
      else:
        registeredSuccessfully = register_user(username=form2.username2.data,email=form2.email2.data,password = hashed_password)
      
  return render_template('login.html', form1=form1,form2=form2,message = message)

def register_user(username,email,password):
  new_user = User(username=username,email=email,password=password)
  db.session.add(new_user)
  db.session.commit()
  return True

@app.route('/deleteid/<int:deletedid>',methods=['GET','POST'])
@login_required
def deleteid(deletedid):
  if request.method == 'POST':
    sqlite_insert_query = """delete from upload
                            where doctoremail = ? and id = ? ;"""
    data_tuple = (current_user.email,deletedid,)
    conn = sqlite3.connect(databasename, uri=True)
    cur = conn.cursor()
    cur.execute(sqlite_insert_query,data_tuple)
    conn.commit()
    conn.close()
  return redirect(url_for('dashboard'))

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
  
  resultlast=""
  manufactures=[]
  manufacturer=[]
  # print(current_user.username)
  form3 = UploadForm()
  if form3.validate_on_submit():   #اعرفي استخدامها 
    
    if request.method == 'POST':
      # check if the post request has the file part
      if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
      # get the implant image  
      file = request.files['file']
      # if user does not select file, browser also
      # submit a empty part without filename
      if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) 
        imagename = current_user.username + "_" + datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + "_" +filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], imagename))
        manufacturer = np.round(getImplantType(app.config['UPLOAD_FOLDER'], imagename,int(form3.bw_lvl.data))*100)
        manufactures =['strau','astra','b_b']
        
       # for i in range(3):
       #   resultlast = resultlast +"\n"+"\n"+ manufactures[i] + " " + str(round(manufacturer[0][i] * 100)) + "% \n \n \n"+"\n"+"\n"

        indexmax = np.argmax(manufacturer)
        #resultlast = manufactures[indexmax] + " " + str(round(manufacturer[0][indexmax] * 100)) + "%"
        new_upload = Upload(imagename=imagename,doctoremail=current_user.email, patientname=form3.patientname.data,patientemail=form3.patientemail.data,comment=form3.comment.data,bw_lvl=int(form3.bw_lvl.data),manufacturer=str(manufacturer[0]),topman=str(manufactures[indexmax]))
        db.session.add(new_upload)
        db.session.commit() 
  # images = Upload.query.filter_by(email=current_user.email).first()
  sqlite_insert_query = """select * from upload
                            where doctoremail = ? ORDER BY id DESC;"""
  data_tuple = (current_user.email,)
  conn = sqlite3.connect(databasename, uri=True)
  cur = conn.cursor()
  cur.execute(sqlite_insert_query,data_tuple)
  data = cur.fetchall()
  conn.close()
  return render_template('dashboard.html',form3=form3,data=data,resultlast=manufactures,shahad=manufacturer)


########function #########
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'static/implants/'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

# @app.route('/register',methods=['GET','POST'])
# def register():
#   form = RegisterForm()
#   if form.validate_on_submit():
#     hashed_password = bcrypt.generate_password_hash(form.password.data)
#     new_user = User(username=form.username.data,email=form.email.data,password = hashed_password)
#     db.session.add(new_user)
#     db.session.commit() 

#     print(f'Succesfully Created User Table {form.email.data}')
#     return redirect(url_for('login'))
#   return render_template('register.html',form=form)

if __name__ == '__main__':
  app.run(debug=True,host="0.0.0.0",use_reloader=True)

#  https://www.sqlite.org/download.html
#   sqlite3 _database.db 
# select * from user
