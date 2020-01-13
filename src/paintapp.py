from tkinter import *
from tkinter.colorchooser import askcolor
import tkinter.font
import webcolors
import requests
import json
import base64
import zlib
from io import BytesIO
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import hashlib
import io
import words
import imagemanipulate
import cryptostuff
import postsandgets
import time
import random
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os.path
from os import path

class PaintApp:

    # Stores current drawing tool used
    drawing_tool = "pencil"

    # Tracks whether left mouse is down
    left_but = "up"

    # x and y positions for drawing with pencil
    x_pos, y_pos = None, None

    #hardcoded blockhash for now will change when blockchain is added
    blockhash = '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824' 

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
        
    def getImageList(self):
        counter = 0
        imageFileNameList = []
        cookies = self.login()
        response = requests.get('http://163.172.168.41:8888/services/files/list/newdir', cookies=cookies)
        jsonresponse  = json.loads(response.text)
        jsonresponse = jsonresponse['fileInfo']

        while len(jsonresponse)!= counter:
            imageFileNameList.append(jsonresponse[counter]['filePath'])
            counter += 1
            pass
        self.imageFileNameList = imageFileNameList

    def fetchImages(self):
        self.loadedimages = []

        imageFileNameList = self.imageFileNameList
        counter = 0
        cookies = self.login()
        while len(imageFileNameList) != counter:
            self.loadedimages.append(requests.get('http://163.172.168.41:8888/services/files/download/newdir/' + imageFileNameList[counter], cookies=cookies))

            counter += 1
            pass
    
    def verifyimages(self):
        counter = 0 
        while len(self.loadedimages) != counter:

            imageJSON = self.loadedimages[counter].content.decode('utf-8')
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
                self.loadedimages.remove(counter)
                counter += 1
                continue

            counter += 1 
            pass

    def onselect(self,evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])

        imageJSON = self.loadedimages[index].content.decode('utf-8')
        imageJSON = json.loads(imageJSON)

        imageJSON['imageRawBytes'] = imageJSON['imageRawBytes'].encode('utf-8')
        imageJSON['imageRawBytes'] = base64.decodebytes(imageJSON['imageRawBytes'])
        imageJSON['imageRawBytes'] = zlib.decompress(imageJSON['imageRawBytes'])
        
        bytesImage = io.BytesIO(base64.b64decode(imageJSON['imageRawBytes']))

        self.img = ImageTk.PhotoImage(Image.open(bytesImage))
        self.viewingcanvas.create_image(20,20,anchor=NW, image=self.img)  

        derivedwords = words.getWordsFromNonceHash(imageJSON['nonce'],imageJSON['blockHash'])
       
        self.verifytextarea.config(state=NORMAL)
        self.verifytextarea.delete('1.0', END)
        self.verifytextarea.insert(tkinter.END, derivedwords,'center-big')
        self.verifytextarea.config(state=DISABLED)

        # print ('You selected item %d: "%s"' % (index, value))
        return


    def clear(self, drawing_area):
        drawing_area.delete('all')
        self.finishedgate = False

    
    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor()[1]

    def humanmade(self):
        
        if self.finishedgate == False:
            messagebox.showinfo("Unordered Action","You need to finalize your drawing before you can vote")
            return

        commit = self.commit(True)
        self.readyToGo['commit'] = commit
        postsandgets.uploadfile(self.nonce, self.readyToGo)

    def nothumanmade(self):

        if self.finishedgate == False:
            messagebox.showinfo("Unordered Action","You need to finalize your drawing before you can vote")
            return

        commit = self.commit(False)
        self.readyToGo['commit'] = commit
        postsandgets.uploadfile(self.nonce, self.readyToGo)

    def commit (self, descion):

        #Commit stage of commit reveal voting, save reveal info in revealdata for a later point

        commitNonce = str(random.getrandbits(64))
        commitTimestamp = str(int(time.time()))
        descion = str(descion)
        commit = commitNonce + '||' + commitTimestamp +'||'+ descion
        self.revealdata = commit
        commit = commit.encode('utf-8')
        commit = hashlib.blake2b(commit).hexdigest()

        return commit

    def refreshlist(self, mylistbox):
        counter = 0
        #compare current image list with newly fetched image list, if difference download all images again
        formerImagelist = []
        formerImagelist = self.imageFileNameList
        self.getImageList()

        if formerImagelist != self.imageFileNameList:
            self.fetchImages() # need to create a fuction that only requests the difference between the two lists and appends the new images, this downloads all imgs again
            pass

        mylistbox.delete(0,'end')
        while counter != len(self.imageFileNameList):
            mylistbox.insert(counter,self.imageFileNameList[counter])
            counter += 1
            pass
        
        return


    def __init__(self, root):

        root.geometry("1250x650")

        #Set default finished value to false
        self.finishedgate = False

        #GenerateKeys
        cryptostuff.generateOrLoadKeypair(self)

        #Pre fetch images for verification
        self.getImageList()
        self.fetchImages()
        self.verifyimages()
        
        #tabs

        style = ttk.Style()

        style.theme_create( "MyStyle", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
        "TNotebook.Tab": {"configure": {"padding": [17, 17] },}})

        style.theme_use("MyStyle")

        

        tabcontrol = ttk.Notebook(root)
        self.tab1 = ttk.Frame(tabcontrol)
        tabcontrol.add(self.tab1, text="Step 1")
        tab2 = ttk.Frame(tabcontrol)
        tabcontrol.add(tab2, text="Step 2")
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
        

        save_button = Button(toolbar, image=save_icon, command= lambda: imagemanipulate.save(self,drawing_area))
        newwords_button = Button(toolbar, image=newwords_icon, command =lambda: words.getNewWords(self,textarea))
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
        textarea.insert(tkinter.END, words.randomWords(self),'center-big')
        textarea.config(state=DISABLED)
        self.color = '#000000'

        #Create text area for verification 
        self.verifytextarea =  Text(tab2)
        self.verifytextarea.tag_configure('center-big', wrap=WORD, justify='center', font=('Verdana', 20, 'bold')) 
        

        #Create viewing canvas in prep to be accept mapping from listbox

        self.viewingcanvas = Canvas(tab2, bd=2, highlightthickness=1, relief='ridge')

        
     # Add list box for verification

        listboxframe= Frame(tab2,bd=1,relief = RAISED)

        counter = 0
        listbox = Listbox(listboxframe)
        while counter != len(self.imageFileNameList):
            listbox.insert(counter,self.imageFileNameList[counter])
            counter += 1
            pass
        listbox.bind('<<ListboxSelect>>', self.onselect)
        listbox.select_set(0)
        listbox.event_generate("<<ListboxSelect>>")

        refresh_img = Image.open("refresh.png")
        refresh_icon = ImageTk.PhotoImage(refresh_img)
        refresh_button = Button(listboxframe, image=refresh_icon, command =lambda: self.refreshlist(listbox))
        refresh_button.image = refresh_icon
        refresh_button.pack (side=tkinter.BOTTOM, padx=2, pady=2)

        listbox.pack()
        listboxframe.pack(side = LEFT)

        #buttons for verification panel 

        bottomframe= Frame(tab2,bd=1,relief = RAISED)

        tick_img = Image.open("tick.png")
        tick_icon = ImageTk.PhotoImage(tick_img)
        tick_button = Button(bottomframe, image=tick_icon, command =lambda: self.humanmade())
        tick_button.image = tick_icon
        tick_button.pack (side=tkinter.LEFT, anchor=tkinter.CENTER, padx=2, pady=2)

        cross_img = Image.open("cross.png")
        cross_icon = ImageTk.PhotoImage(cross_img)
        cross_button = Button(bottomframe, image=cross_icon, command =lambda: self.nothumanmade())
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