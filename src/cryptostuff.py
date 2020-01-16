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

    #Commit stage of commit reveal voting, save reveal info in revealdata for a later point

    commitNonce = str(random.getrandbits(64))
    commitTimestamp = str(int(time.time()))
    descion = str(descion)
    commit = commitNonce + '||' + commitTimestamp +'||'+ descion 
    selfobj.revealdata = commit
    commit = commit.encode('utf-8')
    commit = hashlib.blake2b(commit).hexdigest()

    return commit

def reveal(selfobj):
    revealTimestamp = str(int(time.time()))
    reveal = revealTimestamp + '||' + selfobj.nonce + '||' + selfobj.revealdata + '||' + selfobj.imagehash
    signature = signString(selfobj, reveal)

    revealwithsig  = reveal + '!!!!!!!' + signature

    return revealwithsig

def calculateRound():
    #as long as the server generates the same timestamp as us this should give us information about the currently running round, including whether the round
    #is a commit or reveal round and what time that round ends
    timeinfoarray = []
    currenttimestamp = int(time.time())
    timepaststart = (currenttimestamp - 1579097000)/600 #decided we will start here, we could just start from 0, but i wanted to start here 
    
    if math.floor(timepaststart) % 2 == 0:
        currentround = 'Commit'
        pass
    else:
        currentround = 'Reveal'
        pass

    timepaststart =  timepaststart % 1 
    timepaststart = timepaststart * 600
    timepaststart = 600 - timepaststart

    timeinfoarray.append(int(timepaststart))
    timeinfoarray.append(currentround)
    return timeinfoarray

def verifyimages(selfobj):
    counter = 0 
    while len(selfobj.loadedimages) != counter:

        imageJSON = selfobj.loadedimages[counter].content.decode('utf-8')
        imageJSON = json.loads(imageJSON)

        imageJSON['singature'] = imageJSON['singature'].encode('utf-8')
        imageJSON['singature'] = base64.decodebytes(imageJSON['singature'])
        
        singeddata = imageJSON['public_key'] +'||'+ str(imageJSON['timestamp']) +'||'+ imageJSON['nonce'] +'||'+ imageJSON['imageHash'] +'||'+ imageJSON['blockHash']
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

        counter += 1 
        pass

        