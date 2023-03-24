from flask import Flask
import requests

app = Flask(__name__)

allArtistURL = "http://www.wikiart.org/en/App/Artist/AlphabetJson?v=new&inPublicDomain={true/false}"

@app.route('/')
def hello_world():
    r = requests.get(url = allArtistURL)
    data = r.json()
    return data