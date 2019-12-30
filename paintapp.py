from tkinter import *
import tkinter.font
import webcolors
from PIL import Image, ImageTk, ImageDraw
import random


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
        counter = 0 
        Randomwordarray = []
        with open('concretenounwordlist.txt') as f:
            wordlist = f.read().splitlines() 

        while counter != 6:
            Randomwordarray.append(random.choice(wordlist))
            counter +=1 
            pass
        
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
                event.widget.create_line(self.x_pos, self.y_pos, event.x, event.y, fill='#a2a832', smooth=TRUE)
                self.draw.line(((self.x_pos,self.y_pos),(event.x,event.y)),(0,64,0),width=3)

            self.x_pos = event.x
            self.y_pos = event.y   

    def getNewWords(self, textarea, event=None):
        textarea.config(state=NORMAL)
        textarea.delete('1.0', END)
        textarea.insert(tkinter.END, self.randomWords(),'center-big')
        textarea.config(state=DISABLED)

    def save(self):
        filename = "temp.jpg"
        self.image.save(filename)

    def clear(self, drawing_area):
        drawing_area.delete('all')
        self.image=Image.new("RGB",(drawing_area.winfo_width(),drawing_area.winfo_height()),(255,255,255))
        self.draw=ImageDraw.Draw(self.image)


    def __init__(self, root):

        # Add buttons for Finishing getting new word combos and clearing the canvas

        toolbar = Frame(root,bd=1,relief = RAISED)
        save_img = Image.open("save.png")
        newwords_img = Image.open("newwords.png")
        clearcanvas_img = Image.open("clearcanvas.png")

        save_icon = ImageTk.PhotoImage(save_img)
        newwords_icon = ImageTk.PhotoImage(newwords_img)
        clearcanvas_icon = ImageTk.PhotoImage(clearcanvas_img)

        save_button = Button(toolbar, image=save_icon, command= self.save)
        newwords_button = Button(toolbar, image=newwords_icon, command =lambda: self.getNewWords(textarea))
        clearcanvas_button = Button(toolbar, image=clearcanvas_icon, command = lambda: self.clear(drawing_area))
        
        save_button.image = save_icon
        newwords_button.image = newwords_icon
        clearcanvas_button.image = clearcanvas_icon

        save_button.pack (side = LEFT, padx=2, pady=2)
        newwords_button.pack (side = LEFT, padx=2, pady=2)
        clearcanvas_button.pack (side = LEFT, padx=2, pady=2)

        toolbar.pack(side = TOP, fill= X)
    
      # Add drawing area

        drawing_area = Canvas(root, bd=2, highlightthickness=1, relief='ridge')
        drawing_area.pack(side = LEFT, fill="both", expand=True)
        drawing_area.bind("<Motion>", self.motion)
        drawing_area.bind("<ButtonPress-1>", self.left_but_down)
        drawing_area.bind("<ButtonRelease-1>", self.left_but_up)

      # Add Text Area for displaying word combos

        textarea =  Text(root)
        textarea.pack( side = RIGHT )
        textarea.tag_configure('center-big', justify='center', font=('Verdana', 20, 'bold')) 
        textarea.insert(tkinter.END, self.randomWords(),'center-big')
        textarea.config(state=DISABLED)

      # Create a PIL copy of the image im drawing
        root.update()
        self.image=Image.new("RGB",(drawing_area.winfo_width(),drawing_area.winfo_height()),(255,255,255))
        self.draw=ImageDraw.Draw(self.image)


        hexcolour = webcolors.hex_to_rgb('#a2a832')
        print(hexcolour)

  
root = Tk()

paint_app = PaintApp(root)

root.mainloop()