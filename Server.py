from flask import Flask
import requests
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import numpy as np

openai.api_key = "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"

cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gezivr-7dc1c-default-rtdb.europe-west1.firebasedatabase.app'
    })
ref = db.reference('/')

app = Flask(__name__)

#TO DO: suggested muze idlerinden sanatci isimlerini cekip unityde onerileri goster


def getVisitedMuseumsMatrix(users, museumsIds):   
    lenMuseums = len(museumsIds)
    lenUsers = len(users)
    ratings = np.zeros([lenUsers, lenMuseums])
    i = 0
    for user in users:
        ratings[i] = np.zeros(lenMuseums)
        visitedMuseums = users[user]["visitedMuseums"]
        if visitedMuseums != "" and visitedMuseums is not None:
            for museum in visitedMuseums.values():
                for k in range(lenMuseums):
                    if museumsIds[k] == int(museum["museumId"]):
                        ratings[i][k] = 1 * float(museum["duration"])
                        break
        i = i + 1   
    return ratings

def findMostSimilarUsers(ratings, index):
    userRatings = ratings[index]
    similarity = []
    print("index: " + str(index))
    for i in range(len(ratings)):
        print( "bbb" + str(np.linalg.norm(userRatings) * np.linalg.norm(ratings[i])))
        print(np.dot(userRatings, ratings[i]) / (np.linalg.norm(userRatings) * np.linalg.norm(ratings[i])))
        similarity.append(np.dot(userRatings, ratings[i]) / (np.linalg.norm(userRatings) * np.linalg.norm(ratings[i])))

    return sorted(range(len(similarity)), key = lambda sub: similarity[sub])[-11:]

@app.route("/suggestMuseum")
def suggestMuseum():
    allArtistURL = "http://www.wikiart.org/en/App/Artist/AlphabetJson?v=new&inPublicDomain={true/false}"
    r = requests.get(url = allArtistURL)
    allArtists = r.json()
    #artistlerin contentIdlerini al, bunlar muze idleri olacak
    museumsIds = []
    for artist in allArtists:
        museumsIds.append(artist["contentId"])

    users = ref.child("users").get()
    #rowlar userlar, columnlar muze idleri 1-0 matrisi
    ratings = getVisitedMuseumsMatrix(users, museumsIds)
        
    i=0
    for user in users:
        toBeSuggested = []
        similarUsers = findMostSimilarUsers(ratings, i)
        for similarUser in similarUsers:
            if similarUser != i:
                ratingsOfSimilar = ratings[similarUser]
                for j in range(len(ratingsOfSimilar)):
                    if ratingsOfSimilar[j] !=0 and ratings[i][j] == 0:
                        toBeSuggested.append(museumsIds[j])
        ref.child("users").child(user).child("suggestedMuseums").set(toBeSuggested)          
        i = i + 1
    return "Done"

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

@app.route('/addVisitedMuseum/<userId>/<museumId>/<duration>')
def putMuseum(userId, museumId, duration):    
    visitedMuseums = ref.child("users").child(str(userId)).child("visitedMuseums").get()
    if(visitedMuseums != "" and visitedMuseums is not None):
        for key in visitedMuseums.keys():
            if visitedMuseums[key]["museumId"] == str(museumId):
                #make float

                duration_total = float(visitedMuseums[key]["duration"])
                duration_total += float(duration)
                ref.child('users').child(str(userId)).child('visitedMuseums').child(key).child('duration').set(duration_total)
                return "Sure arttirildi"
            
    
    ref.child('users').child(str(userId)).child('visitedMuseums').push({"museumId":str(museumId), "duration":float(duration)})

    return "Muze eklendi"

@app.route('/getRecommendedMuseums/<userId>')
def getRecommendedMuseums(userId):
    recommendedMuseums = ref.child("users").child(str(userId)).child("suggestedMuseums").get()
    print(type(recommendedMuseums))
    return recommendedMuseums

#if __name__ == '__main__':
# app.run()