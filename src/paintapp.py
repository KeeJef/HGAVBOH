from tkinter import *
from tkinter.colorchooser import askcolor
import tkinter.font
import webcolors
import requests
import json
from io import BytesIO
from tkinter import ttk
from types import SimpleNamespace as Namespace
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import hashlib
import io
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

        concatValue = public_key +'||'+ timestamp +'||'+ nonce +'||'+ imagehash +'||'+ blockhash + '||'
        singedConcat = self.signHashes(concatValue)
        self.exitImageExif(singedConcat)
        
        

    def exitImageExif(self, singedInfo):

        singedInfoString = str(singedInfo[0])
        singedInfoString += "!!!!!!" + str(singedInfo[1]) # Something happens here which fucks with my Public key formattingpyth
        
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
        self.imageFileNameList = imageFileNameList
        counter = 0
        while len(imageFileNameList) != counter:
            self.loadedimages.append(requests.get('http://163.172.168.41:8888/services/files/download/newdir/' + imageFileNameList[counter], cookies=cookies))

            counter += 1
            pass
    
    def verifyimages(self):
        counter = 5 

        while len(self.loadedimages) != counter:

            exifdata = self.dumpRelevantExit((BytesIO(self.loadedimages[counter].content)))
            bytesexifdata = self.dumpExifDataBytes((BytesIO(self.loadedimages[counter].content)))
            signatures = exifdata[0]
            signaturessplit = signatures.split("!!!!!!")
            
            signaturekey = signaturessplit[1]
            signaturekey= signaturekey[2:]
            signaturekey = bytes(signaturekey, encoding= 'utf-8')
            signaturekey = signaturekey.decode('unicode-escape').encode('ISO-8859-1')

            signatureraw = signaturessplit[0]
            signatureraw= signatureraw[2:][:-1]
            signatureraw = bytes(signatureraw, encoding= 'utf-8')
            signatureraw = signatureraw.decode('unicode-escape').encode('ISO-8859-1')

            publickey = serialization.load_pem_public_key(signaturekey, backend=default_backend())
            publickey.verify(signatureraw,bytesexifdata)
            # Right now just verify the image hash, other values will be relevant later

            exifimagehash = exifdata[3]

            #image = Image.open(self.nonce +".jpeg").tobytes()
            
            testimagehash = Image.open(BytesIO(self.loadedimages[counter].content))
            testimagehash = testimagehash.fp.getvalue()
            
            clearedexif = io.BytesIO()
            piexif.remove(testimagehash, clearedexif)

            testsomething = Image.open(clearedexif).tobytes()

            clearedexif = clearedexif.getvalue()


            actualimagehash =  self.loadedimages[counter].content 





            counter += 1 
            pass

    def onselect(self,evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.img = ImageTk.PhotoImage(Image.open(BytesIO(self.loadedimages[index].content)))
        self.viewingcanvas.create_image(20,20,anchor=NW, image=self.img)  

        exifdata = self.dumpRelevantExit((BytesIO(self.loadedimages[index].content)))
        derivedwords = self.getWordsFromNonceHash(exifdata[2],exifdata[4])
       
        self.verifytextarea.config(state=NORMAL)
        self.verifytextarea.delete('1.0', END)
        self.verifytextarea.insert(tkinter.END, derivedwords,'center-big')
        self.verifytextarea.config(state=DISABLED)

        # print ('You selected item %d: "%s"' % (index, value))
        return

    def dumpRelevantExit(self, im):

        im = Image.open(im)
        exif_dict = piexif.load(im.info["exif"])
        exifdata = exif_dict['Exif'][42032]
        exifdata = exifdata.decode('utf-8')
        exifdata = str(exifdata)
        sectionedExif = exifdata.split("||")
        sectionedExif[4] = sectionedExif[4][:-1]
        return sectionedExif

    def dumpExifDataBytes(self, im):
        im = Image.open(im)
        exif_dict = piexif.load(im.info["exif"])
        exifdata = exif_dict['Exif'][42032]
        exifdata = exifdata.decode('utf-8')
        exifdata = str(exifdata)
        sectionedExif = exifdata.split("!!!!!!")
        sectionedExif[1] = sectionedExif[1][2:][:-1]
        sectionedExif[1] = bytes(sectionedExif[1], encoding= 'utf-8')
        sectionedExif[1] = sectionedExif[1].decode('unicode-escape').encode('ISO-8859-1')

        return sectionedExif[1]

    def clear(self, drawing_area):
        drawing_area.delete('all')

    def getWordsFromNonceHash(self, nonce, hashobj):
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

        #Pre fetch images for verification
        self.fetchImages()
        self.verifyimages()
        
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
        textarea.tag_configure('center-big',wrap=WORD, justify='center', font=('Verdana', 20, 'bold')) 
        textarea.insert(tkinter.END, self.randomWords(),'center-big')
        textarea.config(state=DISABLED)
        self.color = '#000000'

        #Create text area for verification 
        self.verifytextarea =  Text(tab2)
        self.verifytextarea.tag_configure('center-big', wrap=WORD, justify='center', font=('Verdana', 20, 'bold')) 
        

        #Create viewing canvas in prep to be accept mapping from listbox

        self.viewingcanvas = Canvas(tab2, bd=2, highlightthickness=1, relief='ridge')

        
     # Add list box for verification
        counter = 0
        listbox = Listbox(tab2)
        while counter != len(self.imageFileNameList):
            listbox.insert(counter,self.imageFileNameList[counter])
            counter += 1
            pass
        listbox.bind('<<ListboxSelect>>', self.onselect)
        listbox.select_set(0)
        listbox.event_generate("<<ListboxSelect>>")

        listbox.pack(side =LEFT)

        #buttons for verifciation panel 

        bottomframe= Frame(tab2,bd=1,relief = RAISED)

        tick_img = Image.open("tick.png")
        tick_icon = ImageTk.PhotoImage(tick_img)
        tick_button = Button(bottomframe, image=tick_icon)
        tick_button.image = tick_icon
        tick_button.pack (side=tkinter.LEFT, anchor=tkinter.CENTER, padx=2, pady=2)

        cross_img = Image.open("cross.png")
        cross_icon = ImageTk.PhotoImage(cross_img)
        cross_button = Button(bottomframe, image=cross_icon)
        cross_button.image = cross_icon
        cross_button.pack (side = tkinter.RIGHT ,anchor=tkinter.CENTER, padx=2, pady=2)

        bottomframe.pack(side = BOTTOM)

       # Pack viewing canvas

        self.viewingcanvas.pack(side =LEFT, fill="both", expand=True)
        
        #Text Area for verification words 

        
        self.verifytextarea.pack( side = RIGHT )

root = Tk()
root.title('Human Art Generation Interface')
paint_app = PaintApp(root)

root.mainloop()