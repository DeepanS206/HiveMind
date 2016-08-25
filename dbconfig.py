from pymongo import MongoClient

def connect():
  connection = MongoClient("ds161495.mlab.com", 61495)
  handle = connection["hivemind_db"]
  handle.authenticate("deepansaravanan", "********")
  return handle
