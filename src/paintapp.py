from tkinter import *
from tkinter.colorchooser import askcolor
import tkinter.font
import webcolors
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageGrab
import hashlib
import random
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
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

        nonce =  str(random.randint(0, 100000000))
        factornonce = nonce + blockhash
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
        x=root.winfo_rootx()+drawing_area.winfo_x()
        y=root.winfo_rooty()+drawing_area.winfo_y()
        x1=x+drawing_area.winfo_width()
        y1=y+drawing_area.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save("temp.png")

    def clear(self, drawing_area):
        drawing_area.delete('all')
    
    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor()[1]

    def getImages(self):

        print("")

    def generateKeypair(self):

        if not path.exists("privkey.txt"):
            
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            textualPublicKey = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
            textualPrivateKey = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())

            encoding = 'utf-8'
            textualPublicKey = textualPublicKey.decode(encoding)
            textualPrivateKey = textualPrivateKey.decode(encoding)

            f = open("pubkey.txt", "a")
            f.write(textualPublicKey)
            f.close()

            f = open("privkey.txt", "a")
            f.write(textualPrivateKey)
            f.close()
            pass

    def signHashes(self):
        print("")

    def updateImgMetaTags(self):
        print("")


    def __init__(self, root):

        #GenerateKeys
        self.generateKeypair()
        
        #tabs
        tabcontrol = ttk.Notebook(root)
        tab1 = ttk.Frame(tabcontrol)
        tabcontrol.add(tab1, text="Create")
        tab2 = ttk.Frame(tabcontrol)
        tabcontrol.add(tab2, text="Verify")
        tabcontrol.pack(expan = 1,fill = "both")

        # Add buttons for Finishing getting new word combos and clearing the canvas

        toolbar = Frame(tab1,bd=1,relief = RAISED)

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

        drawing_area = Canvas(tab1, bd=2, highlightthickness=1, relief='ridge')
        drawing_area.pack(side = LEFT, fill="both", expand=True)
        drawing_area.bind("<Motion>", self.motion)
        drawing_area.bind("<ButtonPress-1>", self.left_but_down)
        drawing_area.bind("<ButtonRelease-1>", self.left_but_up)

      # Add Text Area for displaying word combos

        textarea =  Text(tab1)
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

    # Canvas for Displaying images for Verfication 

        viewingcanvas = Canvas(tab2, bd=2, highlightthickness=1, relief='ridge')
        viewingcanvas.pack(side = RIGHT, fill="both", expand=True)
        self.img = ImageTk.PhotoImage(Image.open("temp.png"))  
        viewingcanvas.create_image(20,20,anchor=NW, image=self.img)  
        
        
        
          


root = Tk()
root.title('Human Art Generation Interface')
paint_app = PaintApp(root)

root.mainloop()