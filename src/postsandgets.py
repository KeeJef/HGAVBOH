import requests
import json
import sqldatabase
import base64

def login():
    headers = {'Content-Type': 'application/json',}
    data = '{ "userName": "master", "password": "secret" }'
    response = requests.post('http://163.172.168.41:8888/services/auth/login', headers=headers, data=data)
    cookies = response.cookies
    return cookies

def uploadfile(nonce,dataJSON):

        cookies = login()
        dataJSON = json.dumps(dataJSON)
        dataJSON = dataJSON.encode('utf-8')
        files = {'file': (dataJSON),}
        requests.post('http://163.172.168.41:8888/services/files/upload/newdir/'+ nonce + '.json', cookies=cookies, files=files)

def uploadreveal(selfobj, revealJSON):
        cookies = login()
        revealJSON = json.dumps(revealJSON)
        revealJSON = revealJSON.encode('utf-8')
        files = {'file': (revealJSON),}
        requests.post('http://163.172.168.41:8888/services/files/upload/reveal/'+ selfobj.readyToGo['imageHash'] + '.json', cookies=cookies, files=files)


def uploadvotes(selfobj, votesJSON):
        cookies = login()
        votesJSON = json.dumps(votesJSON)
        votesJSON = votesJSON.encode('utf-8')
        files = {'file': (votesJSON),}
        requests.post('http://163.172.168.41:8888/services/files/upload/votes/'+ selfobj.readyToGo['imageHash'] + '.json', cookies=cookies, files=files)


def getRevealList():
    counter = 0
    revealFileNameList = []
    cookies = login()
    response = requests.get('http://163.172.168.41:8888/services/files/list/reveal', cookies=cookies)
    jsonresponse  = json.loads(response.text)
    jsonresponse = jsonresponse['fileInfo']

    while len(jsonresponse)!= counter:
        revealFileNameList.append(jsonresponse[counter]['filePath'])
        counter += 1
        pass
    
    return revealFileNameList

def getReveals(revealFileNameList):

    loadedReveals = []
    counter = 0
    cookies = login()
    while len(revealFileNameList) != counter:
        response =  requests.get('http://163.172.168.41:8888/services/files/download/reveal/' + revealFileNameList[counter], cookies=cookies)
        loadedReveals.append(json.loads(response.text))
        counter += 1
        pass
    return loadedReveals


def getImageList():
    counter = 0
    imageFileNameList = []
    cookies = login()
    response = requests.get('http://163.172.168.41:8888/services/files/list/newdir', cookies=cookies)
    jsonresponse  = json.loads(response.text)
    jsonresponse = jsonresponse['fileInfo']

    while len(jsonresponse)!= counter:
        imageFileNameList.append(jsonresponse[counter]['filePath'])
        counter += 1
        pass
    return imageFileNameList

def getVotelist():
    counter = 0
    voteList = []
    cookies = login()
    response = requests.get('http://163.172.168.41:8888/services/files/list/votes', cookies=cookies)
    jsonresponse  = json.loads(response.text)
    jsonresponse = jsonresponse['fileInfo']

    while len(jsonresponse)!= counter:
        voteList.append(jsonresponse[counter]['filePath'])
        counter += 1
        pass
    return voteList


def getVotes(voteList):
    counter = 0
    loadedVotes = []
    
    cookies = login()
    while len(selfobj.voteList) != counter:
        response =  requests.get('http://163.172.168.41:8888/services/files/download/votes/' + voteList[counter], cookies=cookies)
        loadedVotes.append(json.loads(response.text))
        counter += 1
        pass

    return loadedVotes

def refreshlist(selfobj, mylistbox):
    counter = 0
    #compare current image list with newly fetched image list, if difference download all images again
    formerImagelist = []
    formerImagelist = selfobj.imageFileNameList
    getImageList(selfobj)

    if formerImagelist != selfobj.imageFileNameList:
        fetchImages(selfobj) # need to create a fuction that only requests the difference between the two lists and appends the new images, this downloads all imgs again
        pass

    mylistbox.delete(0,'end')
    while counter != len(selfobj.imageFileNameList):
        mylistbox.insert(counter,selfobj.imageFileNameList[counter])
        counter += 1
        pass
    
    return

def fetchImages(imageFileNameList):
    loadedimages = []
    
    counter = 0
    cookies = login()
    while len(imageFileNameList) != counter:
        response =  requests.get('http://163.172.168.41:8888/services/files/download/newdir/' + imageFileNameList[counter], cookies=cookies)
        loadedimages.append(json.loads(response.text))        
        counter += 1
        pass

    return loadedimages
