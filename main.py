from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from pymysql import apilevel



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://to-do-app:Cuellara2013@localhost:8889/to-do-app'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Task(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120))

  def __init__(self,name):
    self.name = name



@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()
    
    tasks = Task.query.all()

    return render_template('todos.html',title="To Do Application", tasks=tasks)

if __name__ == '__main__':
  app.run()