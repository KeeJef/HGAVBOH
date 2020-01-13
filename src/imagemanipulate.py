import base64
import zlib
from cryptography.hazmat.primitives import serialization
import hashlib
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import time 
import cryptostuff

def save(selfobj, drawing_area):
    x=selfobj.tab1.winfo_rootx()+drawing_area.winfo_x()
    y=selfobj.tab1.winfo_rooty()+drawing_area.winfo_y()
    x1=x+drawing_area.winfo_width()
    y1=y+drawing_area.winfo_height()
    ImageGrab.grab().crop((x,y,x1,y1)).save(selfobj.nonce+".jpeg")
    getImageReady(selfobj)

def getImageReady(selfobj):

    imageJSON = {}

    public_key = selfobj.private_key.public_key()
    public_key= public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
    public_key= public_key.decode('utf-8')

    #image = Image.open(selfobj.nonce +".jpeg" , "rb") #make this a Json field in json

    with open(selfobj.nonce +".jpeg", "rb") as image:
        image = base64.b64encode(image.read())

    imagehash =  hashlib.blake2b(image).hexdigest()       
    
    #Add cryptokeys here 

    imageJSON['public_key'] = public_key
    imageJSON['nonce'] = selfobj.nonce
    imageJSON['timestamp'] = int(time.time())
    imageJSON['blockHash'] = selfobj.blockhash
    imageJSON['imageHash'] = imagehash

    readyToSignString = imageJSON['public_key'] +'||'+ str(imageJSON['timestamp']) +'||'+ imageJSON['nonce'] +'||'+ imageJSON['imageHash'] +'||'+ imageJSON['blockHash'] #Get all values into string for singing
    signature = cryptostuff.signHashes(selfobj, readyToSignString)

    image = zlib.compress(image) #compress image 

    signature = base64.encodebytes(signature)
    image = base64.encodebytes(image)
    
    imageJSON['singature'] = signature.decode('utf-8')
    imageJSON['imageRawBytes'] = image.decode('utf-8')

    selfobj.finishedgate = True
    selfobj.readyToGo = imageJSON