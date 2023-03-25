from flask import Flask
import requests
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

openai.api_key = "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"

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

@app.route("/writeInfoForSkeleton/<skeletonName>")
def writeInfoForSkeleton(skeletonName):
    
    content = "Give information about the " + str(skeletonName);
    messages = [
        {"role": "system", "content" : "You are a kind helpful assistant about museums. You have information about museums, art and dinosaurs."},
    ]
    messages.append({"role": "user", "content": content})

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )

    chat_response = completion.choices[0].message.content
    json = {"description": chat_response, "name": skeletonName, "price": 0, "museum": "", "owner": ""}
    ref.child("pieces").child('skeletons').child(str(skeletonName)).set(json)
    return json

@app.route("/writeInfoForDino/<dinoName>")
def writeInfoForDino(dinoName):
    
    content = "Give information about the " + str(dinoName);
    messages = [
        {"role": "system", "content" : "You are a kind helpful assistant about museums. You have information about museums, art and dinosaurs."},
    ]
    messages.append({"role": "user", "content": content})

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )

    chat_response = completion.choices[0].message.content
    json = {"description": chat_response, "name": dinoName, "price": 0, "museum": "", "owner": ""}
    ref.child("pieces").child('dinosaurs').child(str(dinoName)).set(json)
    return json

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/addVisitedMuseum/<userId>/<museumId>')
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