import json
from flask import Flask, request
from flask_cors import CORS, cross_origin

from anilist import getAniListWatchedList, getRecommendedAnime, updateGenresList
from databaseRequests import getGenres, preCheckUpdateGenreList
from mal import getMalWatchedList

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:3001"]}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods=['POST', 'GET'])
def hello_world():
    return "<p>Hello, CHAT!</p>"

@app.route("/hello", methods=['POST', 'GET'])
def testRequestContextStuff():
    return "<p>Hello, CHAT!</p>"

@app.route("/getGenres", methods=['GET'])
def getGenresRequest():
    #print("allowAdult = ")
    #print(request.query_string)
    #print(request.args.get('allowAdult'))
    if(preCheckUpdateGenreList()):
        updateGenresList()
    genreList = getGenres()
    return genreList

@app.route("/aniRequest", methods=['POST'])
def getRecRequest():
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
    app.run()

def toDict(mediaObj):
    newDict = {}
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