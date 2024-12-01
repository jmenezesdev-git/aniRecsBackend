####mongoDB
import json
import pymongo
from datetime import datetime, timedelta

def preCheckUpdateGenreList():
    if (checkNeedGenreUpdate()):
        return True
    else:
        print("No Need to update Genres List")
        return False


def checkNeedGenreUpdate():
    #If genres was updated in the last hour - return false
    #otherwise return true
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["anirecsdb"]
    myCollection = mydb["genreupdatetime"]
    myExistingTime = myCollection.find()
    for existingTime in myExistingTime:
        print ("Check - existingTime")
        print (existingTime)
        anHourAgo = datetime.now() - timedelta(hours=1)
        if (existingTime["updatedt"] > anHourAgo): #if this is more recent than an hour ago
            return False

    return True
    
def setNeedsGenreUpdate():
    #set the last updated time to the current time
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["anirecsdb"]
    myCollection = mydb["genreupdatetime"]
    myExistingTime = myCollection.find()

    for existingTime in myExistingTime:
        print ("Set - existingTime")
        print (existingTime)
        myCollection.update_one({}, { "$set": {"updatedt" : datetime.now()}})
        return
    x = myCollection.insert_one({"updatedt" : datetime.now()})



def tryAddTagToDB(tag):

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["anirecsdb"]

    myCollection = mydb["genres"]

    myquery = { "id": tag["id"] }

    mydoc = myCollection.find(myquery)

    
    for x in mydoc:
        if x["description"] == tag["description"] and x["isAdult"] == tag["isAdult"] and x["name"] == tag["name"] and x["category"] == tag["category"]:
            return
        else:
            newvalues = { "$set": { "description": tag["description"], "isAdult": tag["isAdult"], "name": tag["name"], "category": tag["category"] } }
            myCollection.update_one(myquery, newvalues)
            return
        

    mydict = { "description": tag["description"], "id": tag["id"], "isAdult": tag["isAdult"], "name": tag["name"], "category": tag["category"] }
    x = myCollection.insert_one(mydict)

def tryAddGenreToDB(genre):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["anirecsdb"]

    myCollection = mydb["genres"]

    myquery = { "name": genre}

    mydoc = myCollection.find(myquery)

    
    for x in mydoc:
        return
        

    mydict = { "description": "", "id": "", "isAdult": "", "name": genre, "category": ""}
    x = myCollection.insert_one(mydict)

def getGenres():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["anirecsdb"]

    myCollection = mydb["genres"]
    mydoc = myCollection.find()

    results = {}
    resultsArr = []
    resultsCount = 0
    for genre in mydoc:
        #print()
        resultsArr.append({"description": genre["description"], "id": genre["id"], "isAdult": genre["isAdult"], "name": genre["name"], "category": genre["category"], "_id": str(genre["_id"])})
        resultsCount += 1
    results = {"data":resultsArr}

    return results

####cassandra

####mySQL