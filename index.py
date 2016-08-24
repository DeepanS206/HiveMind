from flask import Flask, request, session, redirect, render_template, flash, url_for
from authentication import assignUserId, exists
from dbconfig import connect
from bson.objectid import ObjectId
import os

app = Flask(__name__)
handle = connect()
app.config.update(dict(
  SECRET_KEY="development key",
))

@app.context_processor
def override_url_for():
  return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
  if endpoint == 'static':
    filename = values.get('filename', None)
    if filename:
      file_path = os.path.join(app.root_path,
                              endpoint, filename)
      values['q'] = int(os.stat(file_path).st_mtime)
  return url_for(endpoint, **values)

def nameFromUserID(userid):
  user = handle.users.find_one({"userid":userid})
  return user['fullname']

def modifyPosts(posts):
  listPosts = []
  for post in posts:
    post['fullname'] = nameFromUserID(post['userid'])
    listPosts.append(post)
  return listPosts


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
      userId = assignUserId()
      userInfo = {
        "fullname":request.form['fullname'],
        "username":request.form['username'],
        "password":request.form['password'],
        "userid":userId
      }
      if not exists(handle, request.form['username'], userId):
        oid = handle.users.insert(userInfo)
        session['logged_in'] = True
        print 'Welcome to HiveMind ' + request.form['fullname']
        return redirect('/home')
      else:
        error = 'User Info Taken'
  return render_template('add_user.html', error=error)



@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    users = [x for x in handle.users.find()]
    print users
    for user in users:
      if (user['username'] == request.form['username']) and (user['password'] == request.form['password']):
        session['logged_in'] = True
        userInfo = {
          "fullname":user['fullname'],
          "username":user['username'],
          "userid":user['userid']
        }
        session['user'] = userInfo
        print 'log in successful'
        return redirect('/home')
    error = 'Account info not found'
  return render_template('login.html', error=error)




@app.route('/home', methods=['GET'])
def home():
  if session.get('logged_in'):
    userid = session.get('user')['userid']
    userPosts = [x for x in handle.posts.find({"userid":userid})]
    return render_template('home.html', userinfo=session.get('user'), posts=modifyPosts(userPosts))
  else:
    return redirect("/login")


@app.route('/getProfile/<userid>', methods=['GET'])
def getProfile(userid):
  if session.get('logged_in'):
    userId = int(userid)
    #userid = session.get('user')['userid']
    userPosts = [x for x in handle.posts.find({"userid":userId})]
    user = handle.users.find_one({"userid":userId})
    print user
    return render_template('profile.html', userinfo=user, posts=userPosts, userLogged=session.get('user'))
  else:
    return redirect("/login")

@app.route('/postActivity', methods=['POST'])
def postActivity():
  post = request.form['textarea']
  userid = session.get('user')['userid']
  postInfo = {
    'userid':userid,
    'post':post,
    'upvotes':0,
    'downvotes':0
  }
  handle.posts.insert(postInfo)
  return redirect('/')




@app.route('/logout', methods=['GET'])
def logout():
  session.pop('logged_in', None)
  session.pop('user', None)
  flash('you were logged out')
  return redirect('/')




if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)