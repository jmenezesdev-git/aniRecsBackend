import json
import re
import requests
import validators

class MalWatchedList:
  def __init__(self, id, name):
    self.id = id
    self.name = name

class CountData:
    def __init__(self):
        self.countC = 0
        self.countD = 0
        self.countW = 0
        self.countH = 0
        self.countP = 0

def getMalWatchedList(accountNameOrUrl, enableAdultContent):
    accountName = ""
    malWatchedList = []  
    countData = CountData()  
    if (validators.url(accountNameOrUrl)):
        accountName = convertToAccountName(accountNameOrUrl)
    else:
        accountName = accountNameOrUrl
    with open('secrets.json') as jsonFile:
        secretsDict = json.load(jsonFile)
    if(len(secretsDict) > 0):
        aniReqHeader = {'X-MAL-CLIENT-ID':secretsDict["malClientID"], 'Accept':'*/*', 'Accept-Encoding':'gzip, deflate, br', 'Connection':'keep-alive'}


    # https://api.myanimelist.net/v2/users/etherealAffairs/animelist
        if(enableAdultContent == 'true'):
            x = requests.get('https://api.myanimelist.net/v2/users/' + accountName + '/animelist' + '?fields=list_status&limit=50&nsfw=true', headers=aniReqHeader)
        else:
            x = requests.get('https://api.myanimelist.net/v2/users/' + accountName + '/animelist' + '?fields=list_status&limit=50', headers=aniReqHeader)

        if (x.status_code == 200):
            myJson = x.content.decode('utf8').replace("'", '"')
            data = json.loads(myJson)
            #add data to list
            addDataToMalWatchedList(malWatchedList, data["data"], countData)
            #print(data["paging"]["next"])
            if (len(data["data"]) > 0):
                while (len(data["data"]) > 0 and "next" in data["paging"]):
                    x = requests.get(data["paging"]["next"], headers=aniReqHeader)
                    if (x.status_code == 200):
                        myJson = x.content.decode('utf8')
                        data = json.loads(myJson)
                        #add data to list
                        addDataToMalWatchedList(malWatchedList, data["data"], countData)
        else:
            print("Something went wrong")
            print(x.status_code)
            print(x.content)
    # print ("countC" + str(countData.countC))
    # print ("countD" + str(countData.countD))
    # print ("countW" + str(countData.countW))
    # print ("countH" + str(countData.countH))
    # print ("countP" + str(countData.countP))
    print(len(malWatchedList))
    return malWatchedList

def addDataToMalWatchedList(malWatchedList, data, countData):
    if (len(data) > 0):
        for datum in data:
            # if (datum["list_status"]["status"] == "completed"):
            #     countData.countC = countData.countC+1
            # if (datum["list_status"]["status"] == "dropped"):
            #     countData.countD = countData.countD+1
            # if (datum["list_status"]["status"] == "watching"):
            #     countData.countW = countData.countW+1
            # if (datum["list_status"]["status"] == "on_hold"):
            #     countData.countH = countData.countH+1
            # if (datum["list_status"]["status"] == "plan_to_watch"):
            #     countData.countP = countData.countP+1
            if (datum["list_status"]["status"] == "completed" or datum["list_status"]["status"] == "dropped" or datum["list_status"]["status"] == "watching" or datum["list_status"]["status"] == "on_hold"):
                newRow = MalWatchedList(datum["node"]["id"], datum["node"]["title"])
                malWatchedList.append(newRow)


def convertToAccountName(accountNameOrUrl):
    matchList = re.match(r"^(.*/)*([^?]+)(\?.*)?$", accountNameOrUrl)
    if matchList != None:
        return matchList[2]
    return accountNameOrUrl




    #what is quart?