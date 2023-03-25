from flask import Flask
import requests

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gezivr-7dc1c-default-rtdb.europe-west1.firebasedatabase.app'
    })
ref = db.reference('/')

app = Flask(__name__)

allArtistURL = "http://www.wikiart.org/en/App/Artist/AlphabetJson?v=new&inPublicDomain={true/false}"
r = requests.get(url = allArtistURL)
data = r.json()
print(data[0]['artistName'])

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/<name>')
def hello_world(name):    
    users = ref.get("/users")
    ref.child('users').child('id').set({'name': str(name), 'age': 20})
    return users

@app.route('/<userId>/<museumId>')
def putMuseum(userId, museumId):    
    visitedMuseums = ref.child("users").child(str(userId)).child("visitedMuseums").get()
    if(visitedMuseums is not None):
        for museum in visitedMuseums.values():
            if museum == str(museumId):
                return "Bu muze zaten eklenmis"
    ref.child('users').child(str(userId)).child('visitedMuseums').push(str(museumId))

    return visitedMuseums

#if __name__ == '__main__':
#  app.run()