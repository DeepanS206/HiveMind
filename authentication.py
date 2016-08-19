from random import randrange

def assignUserId():
  return randrange(1000000)

def exists(handle, username, userid):
  users = [x for x in handle.users.find()]
  for user in users:
    if (user['username'] == username) or (user['userid'] == userid):
      return True
  return False