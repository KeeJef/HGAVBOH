from tkinter import *
from tkinter.colorchooser import askcolor
import tkinter.font
import webcolors
import requests
import json
from tkinter import ttk
from types import SimpleNamespace as Namespace
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import hashlib
import time
import random
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import piexif
import os.path
from os import path

blockhash = '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824' #hardcoded for now 

class PaintApp:

    # Stores current drawing tool used
    drawing_tool = "pencil"

    # Tracks whether left mouse is down
    left_but = "up"

    # x and y positions for drawing with pencil
    x_pos, y_pos = None, None

    
    # ---------- CATCH MOUSE UP ----------

    def left_but_down(self, event=None):
        self.left_but = "down"

        # Set x & y when mouse is clicked
        self.x1_line_pt = event.x
        self.y1_line_pt = event.y

    # ---------- CATCH MOUSE UP ----------

    def left_but_up(self, event=None):
        self.left_but = "up"

        # Reset the line
        self.x_pos = None
        self.y_pos = None

        # Set x & y when mouse is released
        self.x2_line_pt = event.x
        self.y2_line_pt = event.y

    def randomWords(self, event=None):

        self.nonce =  str(random.randint(0, 100000000))
        factornonce = self.nonce + blockhash
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


    # ---------- CATCH MOUSE MOVEMENT ----------

    def motion(self, event=None):

        if self.drawing_tool == "pencil":
            self.pencil_draw(event)

    # ---------- DRAW PENCIL ----------

    def pencil_draw(self, event=None):
        if self.left_but == "down":

            # Make sure x and y have a value
            if self.x_pos is not None and self.y_pos is not None:
                event.widget.create_line(self.x_pos, self.y_pos, event.x, event.y, fill=self.color, capstyle=ROUND, smooth=TRUE, splinesteps=36, width=self.choose_size_button.get())

            self.x_pos = event.x
            self.y_pos = event.y   

    def getNewWords(self, textarea, event=None):
        textarea.config(state=NORMAL)
        textarea.delete('1.0', END)
        textarea.insert(tkinter.END, self.randomWords(),'center-big')
        textarea.config(state=DISABLED)

    def save(self, drawing_area):
        x=self.tab1.winfo_rootx()+drawing_area.winfo_x()
        y=self.tab1.winfo_rooty()+drawing_area.winfo_y()
        x1=x+drawing_area.winfo_width()
        y1=y+drawing_area.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save(self.nonce+".jpeg")
        self.submitToNetwork()

    def submitToNetwork(self):
        public_key = self.private_key.public_key()
        public_key= public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
        public_key= public_key.decode('utf-8')
        image = Image.open(self.nonce +".jpeg").tobytes()
        imagehash =  hashlib.blake2b(image).hexdigest()
        timestamp = str(int(time.time()))
        nonce = self.nonce
        
        #Add cryptokeys here 

        concatValue = public_key +'|'+ timestamp +'|'+ nonce +'|'+ imagehash +'|'+ blockhash
        singedConcat = self.signHashes(concatValue)
        self.exitImageExif(singedConcat)
        
        

    def exitImageExif(self, singedInfo):

        singedInfoString = str(singedInfo[0])
        singedInfoString += "!!!!!!" + str(singedInfo[1])
        
        exif_ifd = {piexif.ExifIFD.CameraOwnerName: singedInfoString}
        exif_dict = {"Exif":exif_ifd}

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes,self.nonce + ".jpeg")

        self.uploadfile()

    def uploadfile(self):

        headers = {'Content-Type': 'application/json',}
        data = '{ "userName": "master", "password": "secret" }'
        response = requests.post('http://163.172.168.41:8888/services/auth/login', headers=headers, data=data)
        cookies = response.cookies
        files = {'file': (self.nonce+'.jpeg', open( self.nonce +'.jpeg', 'rb')),}
        response = requests.post('http://163.172.168.41:8888/services/files/upload/newdir/'+ self.nonce + '.jpeg', cookies=cookies, files=files)

    def fetchImages(self):
        counter = 0
        imageFileNameList = []
        self.loadedimages = []

        headers = {'Content-Type': 'application/json',}
        data = '{ "userName": "master", "password": "secret" }'
        response = requests.post('http://163.172.168.41:8888/services/auth/login', headers=headers, data=data)
        cookies = response.cookies
        response = requests.get('http://163.172.168.41:8888/services/files/list/newdir', cookies=cookies)
        jsonresponse  = json.loads(response.text)
        jsonresponse = jsonresponse['fileInfo']

        while len(jsonresponse)!= counter:
            imageFileNameList.append(jsonresponse[counter]['filePath'])
            counter += 1
            pass
        counter = 0
        while len(imageFileNameList) != counter:
            self.loadedimages.append(requests.get('http://163.172.168.41:8888/services/files/download/newdir/' + imageFileNameList[counter], cookies=cookies))
            counter += 1
            pass



    def clear(self, drawing_area):
        drawing_area.delete('all')
    
    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor()[1]

    def generateOrLoadKeypair(self):

        encoding = 'utf-8'

        if not path.exists("privkey.txt"):
            
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            textualPublicKey = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
            textualPrivateKey = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())

            textualPublicKey = textualPublicKey.decode(encoding)
            textualPrivateKey = textualPrivateKey.decode(encoding)

            f = open("pubkey.txt", "a")
            f.write(textualPublicKey)
            f.close()

            f = open("privkey.txt", "a")
            f.write(textualPrivateKey)
            f.close()

            self.private_key = private_key

            return

        f=open("privkey.txt", "r")
        if f.mode == 'r':
            contents =f.read()
            pass

        textualPrivateKey = contents.encode(encoding)
        private_key = serialization.load_pem_private_key(data=textualPrivateKey,password=None,backend=default_backend())
        
        self.private_key = private_key


    def signHashes(self, dataToSign):

        dataToSign = str.encode(dataToSign)
        signature = self.private_key.sign(dataToSign)  

        public_key = self.private_key.public_key()      
        public_key.verify(signature, dataToSign)

        signeddata = [signature, dataToSign]

        return signeddata

    def updateImgMetaTags(self):
        print("")


    def __init__(self, root):

        #GenerateKeys
        self.generateOrLoadKeypair()

        #Pre fetch images for verfication
        self.fetchImages()
        
        #tabs
        tabcontrol = ttk.Notebook(root)
        self.tab1 = ttk.Frame(tabcontrol)
        tabcontrol.add(self.tab1, text="Create")
        tab2 = ttk.Frame(tabcontrol)
        tabcontrol.add(tab2, text="Verify")
        tabcontrol.pack(expan = 1,fill = "both")

        # Add buttons for Finishing getting new word combos and clearing the canvas

        toolbar = Frame(self.tab1,bd=1,relief = RAISED)

        save_img = Image.open("save.png")
        newwords_img = Image.open("newwords.png")
        clearcanvas_img = Image.open("clearcanvas.png")
        selectcolour_img = Image.open("selectcolour.png")

        save_icon = ImageTk.PhotoImage(save_img)
        newwords_icon = ImageTk.PhotoImage(newwords_img)
        clearcanvas_icon = ImageTk.PhotoImage(clearcanvas_img)
        selectcolour_icon = ImageTk.PhotoImage(selectcolour_img)

        save_button = Button(toolbar, image=save_icon, command= lambda: self.save(drawing_area))
        newwords_button = Button(toolbar, image=newwords_icon, command =lambda: self.getNewWords(textarea))
        clearcanvas_button = Button(toolbar, image=clearcanvas_icon, command = lambda: self.clear(drawing_area))
        selectcolour_button = Button(toolbar, image=selectcolour_icon, command= self.choose_color)
        self.choose_size_button = Scale(toolbar, from_=1, to=10, orient=HORIZONTAL)

        
        save_button.image = save_icon
        newwords_button.image = newwords_icon
        clearcanvas_button.image = clearcanvas_icon
        selectcolour_button.image = selectcolour_icon

        save_button.pack (side = LEFT, padx=2, pady=2)
        newwords_button.pack (side = LEFT, padx=2, pady=2)
        clearcanvas_button.pack (side = LEFT, padx=2, pady=2)
        selectcolour_button.pack (side = LEFT, padx=2, pady=2)
        self.choose_size_button.pack (side = LEFT, padx=2, pady=2)
        self.choose_size_button.set(5)

        toolbar.pack(side = TOP, fill= X)
    
      # Add drawing area

        drawing_area = Canvas(self.tab1, bd=2, highlightthickness=1, relief='ridge')
        drawing_area.pack(side = LEFT, fill="both", expand=True)
        drawing_area.bind("<Motion>", self.motion)
        drawing_area.bind("<ButtonPress-1>", self.left_but_down)
        drawing_area.bind("<ButtonRelease-1>", self.left_but_up)

      # Add Text Area for displaying word combos

        textarea =  Text(self.tab1)
        textarea.pack( side = RIGHT )
        textarea.tag_configure('center-big', justify='center', font=('Verdana', 20, 'bold')) 
        textarea.insert(tkinter.END, self.randomWords(),'center-big')
        textarea.config(state=DISABLED)
        self.color = '#000000'

        testarray = ["dog","cat","pig"]
        
     # Add list box for verification
        counter = 0
        listbox = Listbox(tab2)
        while counter != len(testarray):
            listbox.insert(counter,testarray[counter])
            counter += 1
            pass
        listbox.pack(side =LEFT)

    # Canvas for Displaying images for Verification 

        viewingcanvas = Canvas(tab2, bd=2, highlightthickness=1, relief='ridge')
        viewingcanvas.pack(side = RIGHT, fill="both", expand=True)
        self.img = ImageTk.PhotoImage(Image.open("temp.jpeg"))  
        viewingcanvas.create_image(20,20,anchor=NW, image=self.img)  
        

root = Tk()
root.title('Human Art Generation Interface')
paint_app = PaintApp(root)

root.mainloop()