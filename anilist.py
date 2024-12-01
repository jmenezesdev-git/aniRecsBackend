import json
import re
import requests
import validators

from databaseRequests import setNeedsGenreUpdate, tryAddGenreToDB, tryAddTagToDB
from mal import MalWatchedList

class AniListWatchedList:
  def __init__(self, id, malid, name, listItemId):
    self.id = id
    self.malid = malid
    self.name = name
    self.listItemId = listItemId

def getAniListWatchedList(anilistAccountOrUrl):
    aniListWatchedList = []
    url = 'https://graphql.anilist.co'

    query = '''
    query ($userName: String) {
    MediaListCollection(userName: $userName, type: ANIME) {
        user {
        id
        }
        lists {
        entries {
            id
            customLists
            hiddenFromStatusLists
            media {
            id
            idMal
            isAdult
            title {
                userPreferred
            }
            }
            mediaId
            status
        }
        name
        status
        }
    }
    }
    '''

    
                # english
                # native
                # romaji

#https://anilist.co/user/etherealAffairs/
    accountName = ""
    if (validators.url(anilistAccountOrUrl)):
        accountName = convertToAccountName(anilistAccountOrUrl)
    else:
        accountName = anilistAccountOrUrl

    variables = {
        'userName': accountName

    }

    response = requests.post(url, json={'query': query, 'variables': variables})
    listItemId = 0
    if (response.status_code == 200):
        myJson = response.content.decode('utf8')
        data = json.loads(myJson)
        for list in data["data"]["MediaListCollection"]["lists"]:
            for entry in list["entries"]:
                if (entry["status"] == "COMPLETED" or entry["status"] == "DROPPED" or entry["status"] == "CURRENT" or entry["status"] == "PAUSED"):
                    tempListItem = AniListWatchedList(entry["media"]["id"], entry["media"]["idMal"], entry["media"]["title"]["userPreferred"], listItemId)
                    aniListWatchedList.append(tempListItem)
                    listItemId = listItemId + 1
            print(len(list["entries"]))
        for item in aniListWatchedList:
            if str(item.id) == "20912":
                print (item.id)
                print (item.listItemId)

        aniListWatchedList[:] = [item for item in aniListWatchedList if determine(item, aniListWatchedList)]
        print("aniListWatchedList length = " + str(len(aniListWatchedList)))

    return []

def determine(listItem, aniListWatchedList):
    presenceCount = 0
    firstId = -1
    for item in aniListWatchedList:
        if listItem.id == item.id:
            if firstId == -1:
                firstId = item.listItemId
            presenceCount = presenceCount + 1
            if presenceCount > 1 and firstId > -1 and firstId != listItem.listItemId:
                print("returning false")
                return 0
         
    return 1

def convertToAccountName(accountNameOrUrl):
    matchList = re.match("^(.*user/)([^/]+)(.*)?$", accountNameOrUrl)
    if matchList != None:
        return matchList[2]
    return accountNameOrUrl

def updateGenresList():
    
    print("Updating Genres List")
    url = 'https://graphql.anilist.co'

    query = '''
    query {
    MediaTagCollection {
        description
        id
        isAdult
        name
        category
    }
    }
    '''

    query2 = '''
    query {
        GenreCollection
    }
    '''
    variables = {}

    response = requests.post(url, json={'query': query, 'variables': variables})

    if (response.status_code == 200):
        # print("It didn't explode!")
        myJson = response.content.decode('utf8')
        data = json.loads(myJson)
        for datum in data["data"]["MediaTagCollection"]:
            tryAddTagToDB(datum)

    else:
        print("Oh no! It exploded!")
        print(response)
        print(response.content)
        print(response.json)

    response2 = requests.post(url, json={'query': query2, 'variables': variables})

    if (response2.status_code == 200):
        # print("It didn't explode!")
        myJson = response2.content.decode('utf8')
        data = json.loads(myJson)
        # print (data)
        for datum in data["data"]["GenreCollection"]:
            tryAddGenreToDB(datum)
    else:
        print("Oh no! It exploded!")
        print(response2)
        print(response2.content)
        print(response2.json)
    setNeedsGenreUpdate()

def getRecommendedAnime(requestInfo, malWatchedList:MalWatchedList, anilistWatchedList:AniListWatchedList):

    print("hello world!")
    
    MWLArray = convertMWLToIntArray(malWatchedList)
    ALArray = convertAWLToIntArray(anilistWatchedList)

    url = 'https://graphql.anilist.co'
    query = '''
    query Media($genreIn: [String], $genreNotIn: [String], $tagIn: [String], $tagNotIn: [String], $idNotIn: [Int], $idMalNotIn: [Int], $isAdult: Boolean, $startDateGreater: FuzzyDateInt, $startDateLesser: FuzzyDateInt) {
    Media(genre_in: $genreIn, genre_not_in: $genreNotIn, tag_in: $tagIn, tag_not_in: $tagNotIn, id_not_in: $idNotIn, idMal_not_in: $idMalNotIn, isAdult: $isAdult, startDate_greater: $startDateGreater, startDate_lesser: $startDateLesser, type: ANIME) {
        averageScore
        coverImage {
        extraLarge
        }
        isAdult
        description
        title {
        userPreferred
        romaji
        english
        }
    }
    }
    '''
    variables = {
        'idNotIn': ALArray,
        'idMalNotIn': MWLArray,
        'isAdult': requestInfo["enableAdultContent"],
        'startDateGreater': requestInfo["minDate"] + "0000",
        'startDateLesser': requestInfo["maxDate"] + "0000"
    }

def convertMWLToIntArray(malWatchedList:MalWatchedList):
    returnArray = []
    for listItem in malWatchedList:
        returnArray.append(listItem.id)
    return returnArray

def convertAWLToIntArray(anilistWatchedList:AniListWatchedList):
    returnArray = []
    for listItem in malWatchedList:
        returnArray.append(listItem.id)
    return returnArray