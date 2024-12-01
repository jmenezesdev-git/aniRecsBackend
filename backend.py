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
    #if (len(malAccount) > 0):
    #    malWatchedList = getMalWatchedList(malAccount, enableAdultContent)
    #if (len(anilistAccount) > 0):
    #    anilistWatchedList = getAniListWatchedList(anilistAccount)

    for filter in genreFilter:
        print (filter)

    getRecommendedAnime(request.json, malWatchedList, anilistWatchedList)

    return {'requestArgs': request.json}

if __name__ == '__main__':
    app.run()