import json
from flask import Flask, request
from flask_cors import CORS, cross_origin
import requests

from anilist import getAniListWatchedList, getRecommendedAnime, updateGenresList
from databaseRequests import getGenres, preCheckUpdateGenreList
from mal import getMalWatchedList
from gcpTasks import createUpdateGenresTask

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": ["etherealcluster.sij5s.mongodb.net", "https://anirecs.web.app", "https://anirecs.firebaseapp.com", "https://anirecs.etherealdev.com", "http://localhost:3000", "http://localhost:3001", "http://localhost:3020", "https://anirecsbackend-951543336432.us-central1.run.app"]}})
app.config['CORS_HEADERS'] = 'Content-Type'





@app.route("/", methods=['POST', 'GET'])
def hello_world():
    return "<p>Hello, CHAT!</p>"

@app.route("/hello", methods=['POST', 'GET'])
def testRequestContextStuff():
    return "<p>Hello, CHAT!</p>"


@app.route("/serverip", methods=['GET'])
def testCurrentIp():
    req = requests.get('https://api.ipify.org?format=json')
    if (req.status_code == 200):
        myJson = req.content.decode('utf8').replace("'", '"')
        data = json.loads(myJson)
        return data
     

@app.route("/getGenres", methods=['GET'])
def getGenresRequest():
    if(preCheckUpdateGenreList()):
        createUpdateGenresTask()
    genreList = getGenres()
    return genreList

@app.route("/updateGenres", methods=['POST'])
def updateGenresRequest():
    if(preCheckUpdateGenreList()):
        updateGenresList()

def toDict(mediaObj):
    newDict = {}
    if (mediaObj != None and mediaObj.id != None):
        newDict["id"] = mediaObj.id
        newDict["malid"] = mediaObj.malid
        newDict["titleEN"] = mediaObj.title["english"]
        newDict["titleUserPref"] = mediaObj.title["userPreferred"]
        newDict["titleRomaji"] = mediaObj.title["romaji"]
        
        newDict["isAdult"] = mediaObj.isAdult
        newDict["coverImage"] = mediaObj.coverImage["extraLarge"]
        newDict["description"] = mediaObj.description
        newDict["startDate"] = mediaObj.startDate
        newDict["averageScore"] = mediaObj.averageScore
        return newDict
    return {}


@app.route("/aniRequest", methods=['POST'])
def getRecRequest():
    print("RESULTS =====")

    malAccount=request.json["malAccount"]
    anilistAccount=request.json["anilistAccount"]
    enableAdultContent=request.json["enableAdultContent"]
    minDate=request.json["minDate"]
    maxDate=request.json["maxDate"]
    genreFilter=request.json["genreFilter"]
    excludedGenreFilter=request.json["excludedGenreFilter"]
    malWatchedList = []
    anilistWatchedList = []
    if (len(malAccount) > 0):
        malWatchedList = getMalWatchedList(malAccount, enableAdultContent)
    if (len(anilistAccount) > 0):
        anilistWatchedList = getAniListWatchedList(anilistAccount)



    rec = getRecommendedAnime(request.json, malWatchedList, anilistWatchedList)
    if rec:
        if rec.title["english"] != None:
            print ("I have a recommendation! It is: " + rec.title["english"])
        else:
            print ("I have a recommendation! It is: " + rec.title["userPreferred"])

        return json.dumps(toDict(rec))#{'requestArgs': request.json}
    return {'error': 'Unable to find matching Anime'}

if __name__ == '__main__':
    app.run(host='0.0.0.0')



