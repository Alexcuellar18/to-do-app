from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from pymysql import apilevel
from hashutils import make_pw_hash,check_pw_hash



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://to-do-app:Cuellara2013@localhost:8889/to-do-app'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretkey123'

class Task(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))
  completed = db.Column(db.Boolean, default = False)
  owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

  def __init__(self,name,owner):
    self.name = name
    self.completed = False
    self.owner = owner


class User(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True)
  pw_hash = db.Column(db.String(120))
  tasks = db.relationship('Task', backref='owner')

  def __init__(self,email,password):
    self.email = email
    self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
  allowed_routes = ['login', 'register']
  if request.endpoint not in allowed_routes and'email' not in session:
    return redirect('/login')



@app.route('/login', methods=['POST','GET'])
def login():

  if request.method =='POST':
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and check_pw_hash(password,user.pw_hash):
      session['email'] = email
      flash('Logged In.')
      return redirect('/')
    else:
      flash('User password incorrect, or user does not exist','error')
      
  return render_template('login.html')
    


  return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    verified = request.form['verified']

    #todo validate the users data
    existing_user = User.query.filter_by(email=email).first()
    if not existing_user:
      new_user = User(email,password)
      db.session.add(new_user)
      db.session.commit()
      session['email'] = email

      #Todo - remember the user
      return redirect('/')
    else:
      #todo message that says they already exist in DB
      return "<h1>Duplicate user</h1>"


  return render_template('register.html')


@app.route('/logout')
def logout():
  del session['email']
  return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():

  owner = User.query.filter_by(email = session['email']).first()

  if request.method == 'POST':
    task_name = request.form['task']
    new_task = Task(task_name,owner)
    db.session.add(new_task)
    db.session.commit()
    #code above will pull entry from form and add/commit to the Database
  tasks = Task.query.filter_by(completed=False,owner=owner).all()
  completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()

  return render_template('todos.html',title="To Do Application", tasks=tasks, completed_tasks=completed_tasks)


@app.route('/delete-task', methods=['POST'])
def delete():

  task_id = int(request.form['task-id'])
  task = Task.query.get(task_id)
  task.completed = True
  db.session.add(task)
  db.session.commit()
  return redirect('/')


if __name__ == '__main__':
  app.run()