from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from os import path
import os 
import time
import random
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
    selfobj.revealdata = revealdata
    
    commit = commit.encode('utf-8')
    commit = hashlib.blake2b(commit).hexdigest()

    return commit

def reveal(selfobj):
    revealJSON = {}

    revealJSON['revealTimestamp'] = str(int(time.time()))
    revealJSON['imageNonce'] = selfobj.nonce
    revealJSON['revealCommitNonce'] = selfobj.revealdata['commitNonce']
    revealJSON['revealCommitTimestamp'] = selfobj.revealdata['commitTimestamp']
    revealJSON['revealCommitDecision'] = selfobj.revealdata['descion']
    revealJSON['imageHash'] = selfobj.readyToGo['imageHash']
    revealJSON['voteTarget'] = selfobj.revealdata['voteTarget']

    revealConcat = revealJSON['revealTimestamp'] + revealJSON['imageNonce'] + revealJSON['revealCommitNonce'] + revealJSON['revealCommitTimestamp'] + \
    revealJSON['revealCommitDecision'] + revealJSON['imageHash'] + revealJSON['voteTarget']

    signature = signString(selfobj, revealConcat)
    signature =  base64.encodebytes(signature)
    revealJSON['singature'] = signature.decode('utf-8')

    return revealJSON

def createIsolatedVote():
#this function is intended to create the vote assciated with the commit on the submitter side
#a vote should have the image hash it came from the image its voting for the descision and a signature proving it relates to X image
    voteJSON = {}

    voteJSON['originImageHash'] = selfobj.readyToGo['imageHash']
   # voteJSON['voteForImageHash'] = 
    voteJSON['decision']
    voteJSON['signature']


    pass


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

            loadedRevealsJSON = selfobj.loadedReveals[counter2].copy()
            loadedRevealsJSON['singature'] = loadedRevealsJSON['singature'].encode('utf-8')
            loadedRevealsJSON['singature'] = base64.decodebytes(loadedRevealsJSON['singature'])

            preSignData =  loadedRevealsJSON['revealTimestamp'] + loadedRevealsJSON['imageNonce'] + loadedRevealsJSON['revealCommitNonce'] + \
            loadedRevealsJSON['revealCommitTimestamp'] + loadedRevealsJSON['revealCommitDecision'] + loadedRevealsJSON['imageHash']

            #check commit reveals are stil working as epxected with the vote targets addded
            preRevealData = loadedRevealsJSON['revealCommitNonce'] + loadedRevealsJSON['revealCommitTimestamp'] + loadedRevealsJSON['revealCommitDecision'] + loadedRevealsJSON['voteTarget']
            preRevealData = preRevealData.encode('utf-8')
            preRevealData = hashlib.blake2b(preRevealData).hexdigest()

            preSignData = str.encode(preSignData)

            if imageJSON['imageHash'] == loadedRevealsJSON['imageHash']:

                print("hashmatch")
                publickey.verify(loadedRevealsJSON['singature'],preSignData) # Start back on this with the better encoded commits and reveals
                if imageJSON['commit'] == preRevealData:
                    print ("commit reveal match")

                    selfobj.loadedimages[counter]['nonce'] = loadedRevealsJSON['imageNonce']

                    # if all of this has checked out we need to work out what do with their vote, i think it needs to go into a DB and be released when other people 
                    #majority vote them as gucci
                    pass

                pass

            counter2 += 1 
            pass

        counter += 1 
        pass


        