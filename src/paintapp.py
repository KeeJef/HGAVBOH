from tkinter import *
from tkinter.colorchooser import askcolor
import tkinter.font
import json
import base64
import zlib
from io import BytesIO
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import datetime
import words
import imagemanipulate
import cryptostuff
import postsandgets

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

    def on(self,evt):
        # Note here that Tkinter passes an event object to on()
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

        try:
            derivedwords = words.getWordsFromNonceHash(imageJSON['nonce'],imageJSON['blockHash'])
        except:
            derivedwords = "This Image is still in the Reveal stage"
            pass
       
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

        commit = cryptostuff.commit(self, True)
        self.readyToGo['commit'] = commit
        self.imagehash = self.readyToGo['imageHash']
        postsandgets.uploadfile(self.nonce, self.readyToGo)

    def nothumanmade(self):

        if self.finishedgate == False:
            messagebox.showinfo("Unordered Action","You need to finalize your drawing before you can vote")
            return

        commit = cryptostuff.commit(self,False)
        self.readyToGo['commit'] = commit
        postsandgets.uploadfile(self.nonce, self.readyToGo)

    def countdown(self,param):
        
        self.timer['text'] = datetime.timedelta(seconds=param)
        self.timertext['text'] = self.array[1]
        if param > 0:
            # call countdown again after 1000ms (1s)
            root.after(1000, self.countdown, param-1)
            
        else:
            #if we are in a reveal round and the subission flag is true then we want to initate the reveal process,
            #buttons for submission should intitiate this process
            self.array = cryptostuff.calculateRound()
            if self.finishedgate == True and self.array[1] == 'Reveal':
                postsandgets.uploadreveal(self,cryptostuff.reveal(self))
                pass

            param = self.array[0]
            self.timertext['text'] = self.array[1]
            self.countdown(param)


    def __init__(self, root):

        root.geometry("1250x650")

        #Set default finished value to false
        self.finishedgate = False

        #GenerateKeys
        cryptostuff.generateOrLoadKeypair(self)

        #Pre fetch images for verification
        postsandgets.getImageList(self)
        postsandgets.fetchImages(self)

        postsandgets.getRevealList(self)
        postsandgets.getReveals(self)

        cryptostuff.verifyimages(self)
        
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
        self.timer = Label(toolbar, text="", width=10)
        self.timertext = Label(toolbar, text="", width=10)

        save_img = Image.open("../assets/save.png")
        newwords_img = Image.open("../assets/newwords.png")
        clearcanvas_img = Image.open("../assets/clearcanvas.png")
        selectcolour_img = Image.open("../assets/selectcolour.png")
        
        save_icon = ImageTk.PhotoImage(save_img)
        newwords_icon = ImageTk.PhotoImage(newwords_img)
        clearcanvas_icon = ImageTk.PhotoImage(clearcanvas_img)
        selectcolour_icon = ImageTk.PhotoImage(selectcolour_img)
        

        save_button = Button(toolbar, image=save_icon, command= lambda: imagemanipulate.saveImg(self,drawing_area))
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
        self.timer.pack(side = RIGHT, padx=2, pady=2)
        self.timertext.pack(side = RIGHT, padx=2, pady=2)


        self.array = cryptostuff.calculateRound()
        self.countdown(self.array[0])
        

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
        listbox.bind('<<ListboxSelect>>', self.on)
        listbox.select_set(0)
        listbox.event_generate("<<ListboxSelect>>")

        refresh_img = Image.open("../assets/refresh.png")
        refresh_icon = ImageTk.PhotoImage(refresh_img)
        refresh_button = Button(listboxframe, image=refresh_icon, command =lambda: postsandgets.refreshlist(self,listbox))
        refresh_button.image = refresh_icon
        refresh_button.pack (side=tkinter.BOTTOM, padx=2, pady=2)

        listbox.pack()
        listboxframe.pack(side = LEFT)

        #buttons for verification panel 

        bottomframe= Frame(tab2,bd=1,relief = RAISED)

        tick_img = Image.open("../assets/tick.png")
        tick_icon = ImageTk.PhotoImage(tick_img)
        tick_button = Button(bottomframe, image=tick_icon, command =lambda: self.humanmade())
        tick_button.image = tick_icon
        tick_button.pack (side=tkinter.LEFT, anchor=tkinter.CENTER, padx=2, pady=2)

        cross_img = Image.open("../assets/cross.png")
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