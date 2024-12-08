from flask import Flask, request
import requests
import json

def mainFunc():
    print ("In main func")
    secretsDict = {}
    with open('secrets.json') as jsonFile:
        secretsDict = json.load(jsonFile)
    if(len(secretsDict) > 0):
        #let's start making some basic ass requests oh, yeah, and that oauth stuff. Fun times!
        aniReqHeader = {'content-type': 'application/json', 'X-MAL-CLIENT-ID':secretsDict["malClientID"]}
        aniReqBody = {'q': 'Fullmetal Alchemist', 'limit': 1}
        x = requests.get('https://api.myanimelist.net/v2/anime', data=json.dumps(aniReqBody), headers=aniReqHeader)
        if (x.status_code == 200):
            print("SUCCESS")
            print (x.json)

        else:
            print("Something went wrong")
            print(x.status_code)
            print(x.content)
        #malClientID
        #malSecretID

 #       url = 'https://api.github.com/some/endpoint'
#payload = {'some': 'data'}
#headers = {'content-type': 'application/json'}

#r = requests.post(url, data=json.dumps(payload), headers=headers)
    

# x = requests.get('https://w3schools.com', {test:'text'}, args)
# print(x.status_code)
mainFunc();

#Get anime list 
#main_auth (write:users) client_auth (-) 

#Get anime details
#main_auth (write:users) client_auth (-) 

#Get user anime list
#main_auth (write:users) client_auth (-) 