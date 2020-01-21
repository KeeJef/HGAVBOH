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
    commit = revealdata['commitNonce'] + revealdata['commitTimestamp'] + revealdata['descion']
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

    revealConcat = revealJSON['revealTimestamp'] + revealJSON['imageNonce'] + revealJSON['revealCommitNonce'] + revealJSON['revealCommitTimestamp'] + \
    revealJSON['revealCommitDecision'] + revealJSON['imageHash']

    signature = signString(selfobj, revealConcat)
    signature =  base64.encodebytes(signature)
    revealJSON['singature'] = signature.decode('utf-8')

    return revealJSON

def matchAndValdateReveal():
    pass
    #this fuction needs to match the images in the pool with the reveals and validate if they are singed and correct

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

        imageJSON = selfobj.loadedimages[counter].content.decode('utf-8')
        imageJSON = json.loads(imageJSON)

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
        #the nonce when combined with the blockhash = the commit
        #if both of these check out then we need to add the cleartext image and register their vote in our db (Vote is not yet cast until this image checks out)

        while len(selfobj.loadedReveals) != counter2:

            if imageJSON['imageHash'] == selfobj.loadedReveals[counter2][5]:

                print("hashmatch")
                publickey.verify(selfobj.loadedReveals[counter2][6],str.encode(selfobj.loadedReveals[counter2][7])) # Start back on this with the better encoded commits and reveals

                pass

            counter2 += 1 
            pass

        counter += 1 
        pass


        