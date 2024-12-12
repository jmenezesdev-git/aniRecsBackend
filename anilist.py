import json
import re
import requests
import validators
import random

from databaseRequests import getGenres, setNeedsGenreUpdate, tryAddGenreToDB, tryAddTagToDB
from mal import MalWatchedList

class AniListWatchedList:
  def __init__(self, id, malid, name, listItemId):
    self.id = id
    self.malid = malid
    self.name = name
    self.listItemId = listItemId

class Media:
    def __init__(self, id, malid, title, isAdult, coverImage, description, startDate, averageScore):
        self.id = id
        self.malid = malid
        self.title = title
        self.isAdult = isAdult
        self.coverImage = coverImage
        self.description = description
        self.startDate = startDate
        self.averageScore = averageScore




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
            
        aniListWatchedList[:] = [item for item in aniListWatchedList if determine(item, aniListWatchedList)]
        print("aniListWatchedList length = " + str(len(aniListWatchedList)))

    return aniListWatchedList

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
        myJson = response2.content.decode('utf8')
        data = json.loads(myJson)
        for datum in data["data"]["GenreCollection"]:
            tryAddGenreToDB(datum)
    else:
        print("Oh no! It exploded!")
        print(response2)
        print(response2.content)
        print(response2.json)
    setNeedsGenreUpdate()

def getRecommendedAnime(requestInfo, malWatchedList:MalWatchedList, anilistWatchedList):

    MWLArray = []
    ALArray = []

    try:
        malWatchedList
        MWLArray = convertMWLToIntArray(malWatchedList)
    except NameError:
        MWLArray = [0]

    try:
        anilistWatchedList
        ALArray = convertMWLToIntArray(anilistWatchedList)
    except NameError:
        ALArray = [0]

    genreInList = []
    genreNotInList = []
    tagInList = []
    tagNotInList = []
    page =  1

    genreTagList = getGenres()

    counter = 0

    for excluded in requestInfo["excludedGenreFilter"]:
        for tag in genreTagList["data"]:
            if tag["_id"] == excluded["_id"]:
                if tag["id"] != "":
                    tagNotInList.append(tag["name"])
                else:
                    genreNotInList.append(tag["name"])

    for excluded in requestInfo["genreFilter"]:
        for tag in genreTagList["data"]:
            if tag["_id"] == excluded["_id"]:
                if tag["id"] != "":
                    tagInList.append(tag["name"])
                else:
                    genreInList.append(tag["name"])
    
    print("Final Genre/TagInList")
    print(genreInList)
    print(tagInList)

    #set perPage to 30 for LIVE

    url = 'https://graphql.anilist.co'
    query = '''
    query Media($genreIn: [String], $genreNotIn: [String], $tagIn: [String], $tagNotIn: [String], $idNotIn: [Int], $idMalNotIn: [Int], $isAdult: Boolean, $startDateGreater: FuzzyDateInt, $startDateLesser: FuzzyDateInt, $page: Int) {
    
    Page(page: $page, perPage: 30) {
        pageInfo {
            hasNextPage
        }
    
        media(genre_in: $genreIn, genre_not_in: $genreNotIn, tag_in: $tagIn, tag_not_in: $tagNotIn, id_not_in: $idNotIn, idMal_not_in: $idMalNotIn, isAdult: $isAdult, startDate_greater: $startDateGreater, startDate_lesser: $startDateLesser, type: ANIME, sort: [POPULARITY_DESC, SCORE_DESC]) {
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
            id
            idMal
            startDate {
                day
                month
                year
            }
            relations {
                edges {
                    relationType
                    node{
                        averageScore
                        coverImage {
                            extraLarge
                        }
                        isAdult
                        description
                        title {
                            english
                            romaji
                            userPreferred
                        }
                        id
                        idMal
                        startDate {
                            day
                            month
                            year
                        }
                        genres
                        tags {
                            name
                            id
                        }
                    }
                }
            }
        }
    }
    }
    '''
    if (len(genreInList) == 0):
        genreInList = None
    if (len(tagInList) == 0):
        tagInList = None
    variables = {
            'genreIn': genreInList,
            'genreNotIn': genreNotInList,
            'tagIn': tagInList,
            'tagNotIn': tagNotInList,
            'idNotIn': ALArray,
            'idMalNotIn': MWLArray,
            'isAdult': requestInfo["enableAdultContent"],
            'startDateGreater': requestInfo["minDate"] * 10000,
            'startDateLesser': requestInfo["maxDate"] * 10000,
            'page': page

        }


    if (requestInfo["enableAdultContent"] == True):
        print("Enable Adult Content is True")
        query = setQueryNeutralAdult()
        variables = setVariablesNeutralAdult(genreInList, genreNotInList, tagInList, tagNotInList, ALArray, MWLArray, requestInfo, page)
    else:
        print("Enable Adult Content is not True")
        print (str(requestInfo["enableAdultContent"]))

    print ("ALArray length:" + str(len(ALArray)) )

    

    response = requests.post(url, json={'query': query, 'variables': variables})
    listItemId = 0
    if (response.status_code == 200):
        myJson = response.content.decode('utf8')
        data = json.loads(myJson)
        print("PRE-DATA")
        #print(data)
        
        resultsList = []
        addNewResult = False
        
        for flResult in data["data"]["Page"]["media"]:
            #print(flResult["title"])
            addNewResult = False
            #prequelMatchCheck verifies if prequel is a match and can be used, otherwise returns None
            prequel = prequelMatchCheck(flResult, ALArray, MWLArray, requestInfo, genreInList, genreNotInList, tagInList, tagNotInList)
            if (prequel != None):
                newPotential = findPrequelResultRecursive(prequel, ALArray, MWLArray, requestInfo, genreInList, genreNotInList, tagInList, tagNotInList)
                newResult = Media(newPotential["id"], newPotential["idMal"], newPotential["title"], newPotential["isAdult"], newPotential["coverImage"], newPotential["description"], newPotential["startDate"], newPotential["averageScore"])
                
            else:
                print("PREQUEL? REJECTED")
                newResult = Media(flResult["id"], flResult["idMal"], flResult["title"], flResult["isAdult"], flResult["coverImage"], flResult["description"], flResult["startDate"], flResult["averageScore"])
            skipAppend = False
            for r in resultsList:
                if r.id == newResult.id:
                    skipAppend = True
            if skipAppend == False:  
                resultsList.append(newResult)
        for r in resultsList:
            #Not all Entries have an English title
            if r.title["english"] != None:
                print ("Media Results: " + str(r.id) + " " + r.title["english"])
            else:   
                print ("Media Results: " + str(r.id) + " " + r.title["userPreferred"])
            

        if len(resultsList) > 0:
            return random.choice(resultsList)
        
#prequelMatchCheck verifies if prequel is a match and can be used, otherwise returns None
def prequelMatchCheck(flResult, ALArray, MWLArray, requestInfo, genreInList, genreNotInList, tagInList, tagNotInList):
    for edge in flResult["relations"]["edges"]:
        if edge["relationType"] == "PREQUEL":
            prequelNode = edge["node"]
            if(checkGenreListMatches(prequelNode, genreInList, genreNotInList) and tagListMatches(prequelNode, tagInList, tagNotInList)):
                if(not(ALArrayMatches(prequelNode, ALArray)) and not(MWLArrayMatches(prequelNode, MWLArray)) and requestInfoMatches(prequelNode, requestInfo)):
                    return prequelNode
    return None

def checkGenreListMatches(prequelNode, genreInList, genreNotInList):
    for listItem in prequelNode["genres"]:
        if genreNotInList != None:
            for genreNotIn in genreNotInList:
                if (listItem == genreNotIn):
                    return False
        if genreInList != None:
            found = False
            for genreIn in genreInList:
                if (genreIn == listItem):
                    found=True
            if found == False:
                return False
    return True

def tagListMatches(prequelNode, tagInList, tagNotInList):
    for listItem in prequelNode["tags"]:
        if tagNotInList != None:
            for tagNotIn in tagNotInList:
                if (listItem == tagNotIn["name"]):
                    return False
        if tagInList != None:
            found = False
            for tagIn in tagInList:
                if (tagIn == listItem["name"]):
                    found=True
            if found == False:
                return False
    return True


def ALArrayMatches(prequelNode, ALArray):
    for alItem in ALArray:
        if alItem == prequelNode["id"]:
            return False
    return True

def MWLArrayMatches(prequelNode, MWLArray):
    for MalItem in MWLArray:
        if MalItem == prequelNode["idMal"]:
            return False
    return True

def requestInfoMatches(prequelNode, requestInfo):
    if requestInfo["enableAdultContent"] == False:
        if prequelNode["isAdult"] == True:
                return False
    if prequelNode["startDate"]["year"] < requestInfo["minDate"]:
        return False
    if prequelNode["startDate"]["year"] > requestInfo["maxDate"]:
        return False
    return True


def findPrequelResultRecursive(node, ALArray, MWLArray, requestInfo, genreInList, genreNotInList, tagInList, tagNotInList):
    url = 'https://graphql.anilist.co'
    query='''
    query Media($genreIn: [String], $genreNotIn: [String], $tagIn: [String], $tagNotIn: [String], $mediaId: Int, $isAdult: Boolean, $idNotIn: [Int], $idMalNotIn: [Int], $startDateGreater: FuzzyDateInt, $startDateLesser: FuzzyDateInt) {
    Media(genre_in: $genreIn, genre_not_in: $genreNotIn, tag_in: $tagIn, tag_not_in: $tagNotIn, type: ANIME, sort: [POPULARITY_DESC, SCORE_DESC], id: $mediaId, isAdult: $isAdult, id_not_in: $idNotIn, idMal_not_in: $idMalNotIn, startDate_greater: $startDateGreater, startDate_lesser: $startDateLesser) {
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
        id
        idMal
        startDate {
            day
            month
            year
        }
        relations {
        edges {
            relationType
            node {
                id
                idMal
                isAdult
                coverImage {
                    extraLarge
                }
                description
                startDate {
                    day
                    month
                    year
                }
                title {
                    english
                    romaji
                    userPreferred
                }
                averageScore
            }
        }
        }
    }
    }
    '''

        #get Prequel if any, `return result of calling function with prequel`
        #if no prequel exists, return self

    for edge in node["relations"]["edges"]:
        if edge["relationType"] == "PREQUEL":
            prequelNode = edge["node"]
            #print(prequelNode["title"])
            variables = {
                'genreIn': genreInList,
                'genreNotIn': genreNotInList,
                'tagIn': tagInList,
                'tagNotIn': tagNotInList,
                'idNotIn': ALArray,
                'idMalNotIn': MWLArray,
                'isAdult': requestInfo["enableAdultContent"],
                'startDateGreater': requestInfo["minDate"] * 10000,
                'startDateLesser': requestInfo["maxDate"] * 10000,
                'mediaId': prequelNode["id"] #prequel ID, not node ID
            }
            response = requests.post(url, json={'query': query, 'variables': variables})
            #print("Awaiting Response")
            #Test if Prequel Valid, if so call function recursively with prequel as node
            if (response.status_code == 200):
                myJson = response.content.decode('utf8')
                data = json.loads(myJson)
                print("I have recurred")
                return findPrequelResultRecursive(data["data"]["Media"], ALArray, MWLArray, requestInfo, genreInList, genreNotInList, tagInList, tagNotInList)
            #else return self
            else: 
                #print(response.status_code)
                return node
    return node

                            
def isAppropriate(node, requestInfo):
    if requestInfo["enableAdultContent"] == False:
        if node["isAdult"] == True:
            return False
    if requestInfo["minDate"] * 10000 > genIntDate(node["startDate"]) or requestInfo["maxDate"] * 10000 < genIntDate(node["startDate"]):
            return False
    return True

def seenIt(mediaNode, ALArray, MWLArray):
    for item in ALArray:
        if mediaNode["id"] == item:
            return True

    for item in MWLArray:
        if mediaNode["idMal"] == item:
            return True
    return False


def genIntDate(startDate):
    if startDate != []:
        return int(str(startDate["year"]) + str(startDate["month"]) + str(startDate["day"]))
    else:
        return 0

def convertMWLToIntArray(malWatchedList:MalWatchedList):
    returnArray = []
    for listItem in malWatchedList:
        returnArray.append(listItem.id)
    return returnArray

def convertAWLToIntArray(anilistWatchedList:AniListWatchedList):
    returnArray = []
    for listItem in anilistWatchedList:
        returnArray.append(listItem.id)
    return returnArray

def setQueryNeutralAdult():
    return '''
    query Media($genreIn: [String], $genreNotIn: [String], $tagIn: [String], $tagNotIn: [String], $idNotIn: [Int], $idMalNotIn: [Int], $startDateGreater: FuzzyDateInt, $startDateLesser: FuzzyDateInt, $page: Int) {
    
    Page(page: $page, perPage: 30) {
        pageInfo {
            hasNextPage
        }
    
        media(genre_in: $genreIn, genre_not_in: $genreNotIn, tag_in: $tagIn, tag_not_in: $tagNotIn, id_not_in: $idNotIn, idMal_not_in: $idMalNotIn, startDate_greater: $startDateGreater, startDate_lesser: $startDateLesser, type: ANIME, sort: [POPULARITY_DESC, SCORE_DESC]) {
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
            id
            idMal
            startDate {
                day
                month
                year
            }
            relations {
                edges {
                    relationType
                    node{
                        averageScore
                        coverImage {
                            extraLarge
                        }
                        isAdult
                        description
                        title {
                            english
                            romaji
                            userPreferred
                        }
                        id
                        idMal
                        startDate {
                            day
                            month
                            year
                        }
                    }
                }
            }
        }
    }
    }
    '''

def setVariablesNeutralAdult(genreInList, genreNotInList, tagInList, tagNotInList, ALArray, MWLArray, requestInfo, page):
    return {
        'genreIn': genreInList,
        'genreNotIn': genreNotInList,
        'tagIn': tagInList,
        'tagNotIn': tagNotInList,
        'idNotIn': ALArray,
        'idMalNotIn': MWLArray,
        'startDateGreater': requestInfo["minDate"] * 10000,
        'startDateLesser': requestInfo["maxDate"] * 10000,
        'page': page
    }