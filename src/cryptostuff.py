from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from os import path
import os
import copy 
import collections
import time
import random
import postsandgets
import math
import hashlib
import json
import base64
import zlib

def signString(selfobj, dataToSign):

    dataToSign = str.encode(dataToSign)
    signature = selfobj.private_key.sign(dataToSign)  

    public_key = selfobj.private_key.public_key()      
    public_key.verify(signature, dataToSign)

    signeddata = signature

    return signeddata


def generateOrLoadKeypair(selfobj):

        encoding = 'utf-8'

        if not path.exists('../keys/privkey.txt'):
            
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            textualPublicKey = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
            textualPrivateKey = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())

            textualPublicKey = textualPublicKey.decode(encoding)
            textualPrivateKey = textualPrivateKey.decode(encoding)

            f = open("../keys/pubkey.txt", "a")
            f.write(textualPublicKey)
            f.close()

            f = open("../keys/privkey.txt", "a")
            f.write(textualPrivateKey)
            f.close()

            selfobj.private_key = private_key

            return

        f=open("../keys/privkey.txt", "r")
        if f.mode == 'r':
            contents =f.read()
            pass

        textualPrivateKey = contents.encode(encoding)
        selfobj.private_key  = serialization.load_pem_private_key(data=textualPrivateKey,password=None,backend=default_backend())

def commit (selfobj, descion):
    revealdata = {}
 
    #Commit stage of commit reveal voting, save reveal info in revealdata for a later point

    

    revealdata['commitNonce'] = str(random.getrandbits(64))
    revealdata['commitTimestamp'] = str(int(time.time()))
    revealdata['descion'] = str(descion)

    try:
        revealdata['voteTarget'] = selfobj.loadedimages[selfobj.imagechoice]['imageHash']
        pass
    except:
        revealdata['voteTarget'] = 'FAKE IMAGE HASH'
        pass

    commit = revealdata['commitNonce'] + revealdata['commitTimestamp'] + revealdata['descion'] + revealdata["voteTarget"] 
    
    selfobj.revealdata.append(revealdata)
    
    commit = commit.encode('utf-8')
    commit = hashlib.blake2b(commit).hexdigest()

    return commit

def reveal(selfobj):
    #reveals happen on image submision flags
    revealJSONarray = []
    revealJSON = {}
    counter = 0 

    while len(selfobj.revealdata) != counter:

        revealJSON['revealTimestamp'] = str(int(time.time()))
        revealJSON['imageNonce'] = selfobj.nonce
        revealJSON['revealCommitNonce'] = selfobj.revealdata[counter]['commitNonce']
        revealJSON['revealCommitTimestamp'] = selfobj.revealdata[counter]['commitTimestamp']
        revealJSON['revealCommitDecision'] = selfobj.revealdata[counter]['descion']
        revealJSON['imageHash'] = selfobj.readyToGo['imageHash']
        revealJSON['voteTarget'] = selfobj.revealdata[counter]['voteTarget']

        revealConcat = revealJSON['revealTimestamp'] + revealJSON['imageNonce'] + revealJSON['revealCommitNonce'] + revealJSON['revealCommitTimestamp'] + \
        revealJSON['revealCommitDecision'] + revealJSON['imageHash'] + revealJSON['voteTarget']

        signature = signString(selfobj, revealConcat)
        signature =  base64.encodebytes(signature)
        revealJSON['singature'] = signature.decode('utf-8')

        revealJSONarray.append(revealJSON)
        revealJSON = {}
        

        counter +=1
        pass

    createIsolatedVote(selfobj)
    return revealJSONarray

def createIsolatedVote(selfobj):
#this function is intended to create the vote assciated with the commit on the submitter side
#a vote should have the image hash it came from the image its voting for the descision and a signature proving it relates to X image
    voteJSON = {}
    votearray= []
    counter = 0

    while len(selfobj.revealdata) != counter:

        voteJSON['originImageHash'] = selfobj.readyToGo['imageHash']

        voteJSON['voteForImageHash'] = selfobj.revealdata[counter]['voteTarget']
        voteJSON['decision'] = selfobj.revealdata[counter]['descion']

        presigndata = voteJSON['originImageHash'] + voteJSON['voteForImageHash'] + voteJSON['decision']

        signature = signString(selfobj, presigndata)
        signature =  base64.encodebytes(signature)

        voteJSON['signature'] = signature.decode('utf-8')

        votearray.append(copy.deepcopy(voteJSON))

        counter += 1 

        pass

    postsandgets.uploadvotes(selfobj,votearray)

    pass

def votingCandidates(listofimagevotes,maxvotes,loadedimages):

    # will return an array of image hashes that have never been voted on, or fall below the maxvote threshold

    counter = 0 
    counter2 = 0
    voteArray = []
    loadedImageHashArray = []

    while len(listofimagevotes) != counter :

        specificvote = listofimagevotes[counter]

        while len(specificvote) != counter2:

            voteArray.append(specificvote[counter2]['voteForImageHash'])

            counter2 += 1 
            pass
        
        counter2 = 0
        counter +=1 
        pass

    countedArray = collections.Counter(voteArray)

    validImageHashes = [i for i in countedArray if countedArray[i]<maxvotes] #goes through array returns image hashes with under maxvotes

    for imagehashes in loadedimages:

        loadedImageHashArray.append(imagehashes["imageHash"])

        pass

    uniqueElements = set(loadedImageHashArray) - set(voteArray)
    uniqueElements = list(uniqueElements)
    validImageHashes = validImageHashes + uniqueElements

    return validImageHashes


def calculateRound():
    #as long as the server generates the same timestamp as us this should give us information about the currently running round, including whether the round
    #is a commit or reveal round and what time that round ends
    timeinfoarray = []
    roundtime = 30
    currenttimestamp = int(time.time())
    timepaststart = (currenttimestamp - 1579097000)/roundtime #decided we will start here, we could just start from 0, but i wanted to start here 
    
    if math.floor(timepaststart) % 2 == 0:
        currentround = 'Commit'
        pass
    else:
        currentround = 'Reveal'
        pass

    timepaststart =  timepaststart % 1 
    timepaststart = timepaststart * roundtime
    timepaststart = roundtime - timepaststart

    timeinfoarray.append(int(timepaststart))
    timeinfoarray.append(currentround)
    return timeinfoarray

def verifyimages(selfobj):
    counter = 0 
    while len(selfobj.loadedimages) != counter:
        counter2 = 0
        
        imageJSON  = selfobj.loadedimages[counter].copy()

        imageJSON['singature'] = imageJSON['singature'].encode('utf-8')
        imageJSON['singature'] = base64.decodebytes(imageJSON['singature'])
        
        singeddata = imageJSON['public_key'] + str(imageJSON['timestamp']) + imageJSON['imageHash'] + imageJSON['blockHash']
        singeddata = str.encode(singeddata)
        
        #verify the header data is singed by the contained key 
        publickey = serialization.load_pem_public_key(str.encode(imageJSON['public_key']), backend=default_backend())
        publickey.verify(imageJSON['singature'],singeddata)

        imageJSON['imageRawBytes'] = imageJSON['imageRawBytes'].encode('utf-8')
        imageJSON['imageRawBytes'] = base64.decodebytes(imageJSON['imageRawBytes'])
        imageJSON['imageRawBytes'] = zlib.decompress(imageJSON['imageRawBytes'])
        

        verifyimagehash =  hashlib.blake2b(imageJSON['imageRawBytes']).hexdigest()

        #remove elements where loaded image does not match the image hash
        if verifyimagehash != imageJSON['imageHash']:
            selfobj.loadedimages.remove(counter)
            counter += 1
            continue
        #if reveal imagehash matches an already fetched image then we need to verify - the signature for the reveal matches the fetched image 
        #combine the image nonce + the block hash - this will give you the random words for the image
        #Check that the reveal if reveal commit nonce + reveal commit timestamp and reveal commit descision are added together and hashed if that
        #equals the commit in the immage then the reveal is valid

        #if both of these check out then we need to add the cleartext image and register their vote in our db (Vote is not yet cast until this image checks out)

        while len(selfobj.loadedReveals) != counter2:

            loadedRevealsJSON = copy.deepcopy(selfobj.loadedReveals[counter2])
            counter3 = 0

            while len(loadedRevealsJSON) != counter3:
                
                loadedRevealsJSON[counter3]['singature'] = loadedRevealsJSON[counter3]['singature'].encode('utf-8') #make sure both are indexed lul 
                loadedRevealsJSON[counter3]['singature'] = base64.decodebytes(loadedRevealsJSON[counter3]['singature'])

                preSignData =  loadedRevealsJSON[counter3]['revealTimestamp'] + loadedRevealsJSON[counter3]['imageNonce'] + loadedRevealsJSON[counter3]['revealCommitNonce'] + \
                loadedRevealsJSON[counter3]['revealCommitTimestamp'] + loadedRevealsJSON[counter3]['revealCommitDecision'] + loadedRevealsJSON[counter3]['imageHash'] + loadedRevealsJSON[counter3]['voteTarget']

                #check commit reveals are stil working as epxected with the vote targets addded
                preRevealData = loadedRevealsJSON[counter3]['revealCommitNonce'] + loadedRevealsJSON[counter3]['revealCommitTimestamp'] + loadedRevealsJSON[counter3]['revealCommitDecision'] + loadedRevealsJSON[counter3]['voteTarget']
                preRevealData = preRevealData.encode('utf-8')
                preRevealData = hashlib.blake2b(preRevealData).hexdigest()

                preSignData = str.encode(preSignData)

                if imageJSON['imageHash'] == loadedRevealsJSON[counter3]['imageHash']:

                    print("hashmatch")
                    publickey.verify(loadedRevealsJSON[counter3]['singature'],preSignData) # Start back on this with the better encoded commits and reveals
                    if imageJSON['commit'+str(counter3+1)] == preRevealData:
                        print ("commit reveal match")

                        selfobj.loadedimages[counter]['nonce'] = loadedRevealsJSON[counter3]['imageNonce']

                        # if all of this has checked out we need to work out what do with their vote, i think it needs to go into a DB and be released when other people 
                        #majority vote them as gucci
                        pass

                    pass
                counter3 += 1 
                pass
                
            counter2 += 1 
            pass

        counter += 1 
        pass


        