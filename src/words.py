
import tkinter as tkint 
import random
import hashlib

def randomWords(selfobj, event=None):

    selfobj.nonce =  str(random.randint(0, 100000000))
    factornonce = selfobj.nonce + selfobj.blockhash
    factornonce = factornonce.encode('utf-8')
    hashseed = hashlib.blake2b(factornonce)
    hashseed = hashseed.hexdigest()
    random.seed(hashseed)

    Randomwordarray = []
    with open('concretenounwordlist.txt') as f:
        wordlist = f.read().splitlines() 

    Randomwordarray = random.sample(wordlist, k=6)
    randomString = ' '.join(Randomwordarray)

    return randomString

def getNewWords(selfobj, textarea, event=None):
    textarea.config(state=tkint.NORMAL)
    textarea.delete('1.0', tkint.END)
    textarea.insert(tkint.END, randomWords(selfobj),'center-big')
    textarea.config(state=tkint.DISABLED)
    selfobj.finishedgate = False

def getWordsFromNonceHash(nonce, hashobj):
    factornonce = nonce + hashobj
    factornonce = factornonce.encode('utf-8')
    hashseed = hashlib.blake2b(factornonce)
    hashseed = hashseed.hexdigest()
    random.seed(hashseed)

    Randomwordarray = []
    with open('concretenounwordlist.txt') as f:
        wordlist = f.read().splitlines() 

    Randomwordarray = random.sample(wordlist, k=6)
    randomString = ' '.join(Randomwordarray)

    return randomString