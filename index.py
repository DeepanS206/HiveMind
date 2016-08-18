from flask import Flask, request, session, redirect, render_template, flash, url_for
from dbconfig import connect
from bson import objectid
import json
import os

app = Flask(__name__)
handle = connect()
app.config.update(dict(
  SECRET_KEY="development key",
))

@app.route('/', methods=['GET'])
def middleware():
  if session.get('logged_in'):
    return redirect('/home')
  return redirect('/login')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
  error = None
  if request.method == 'POST':
    if request.form['fullname'].strip() == "":
      error = 'Need to register with your full name'
    elif request.form['username'].strip() == "":
      error = 'Need to register with user name'
    elif request.form["password"].strip() == "":
      error = 'Need to register with user name'
    else:
      userInfo = {
        "fullname":request.form['fullname'],
        "username":request.form['username'],
        "password":request.form['password']
      }
      #print(json.dumps(userInfo))
      oid = handle.users.insert(userInfo)
      session['logged_in'] = True
      print 'welcome to HiveMind ' + request.form['fullname']
      return redirect('/home')
  return render_template('add_user.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    users = [json.loads(x) for x in handle.users.find()]
    #print users
    for user in users:
      if (user['username'] == request.form['username']) and (user['password'] == request.form['password']):
        session['logged_in'] == True
        print 'log in successful'
        return redirect('/home')
    error = 'Account info not found'
  return render_template('login.html', error=error)

@app.route('/home', methods=['GET'])
def home():
  return render_template('home.html')

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)