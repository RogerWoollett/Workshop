# A program to calculate values for a dividing 
# head or rotary table.
# written by Roger Woollett

import sys
if sys.version_info[0] > 2:
    import tkinter as tk
    import tkinter.messagebox as msg
else:
    import Tkinter as tk
    import tkMessageBox as msg
    
# Note python 2 and 3 evaluate division of two intergers differently
# Pyhon 2 makes 1/2 = 0 python 3 makes 1/2 = 0.5
# I had to use float in a number of expressions to get compatibility

# These values can be changed if rquired
MAX_PLATES = 4
FRAME_WIDTH = 400
FRAME_HEIGHT = 200
# used to avoid rounding errors
TOLERANCE = 0.000000001

FILENAME = "div.data"

class Data:
    # class object to hold the data and read/write it to disc
    def __init__(self):
        self.valid = False
        self.worm = 0
        self.plate = list()
           
    def read(self,filename):
    # read a configuratin from disc. format is assumed correct
        try:
            file = open(filename)
        except:
            self.valid = False
            return False
        
        # get worm ratio
        line = file.readline()
        self.worm = int(line)
        
        # clear data (there is no clear in pyhon 2.7
        # self.plate.clear()
        del self.plate[:]
          
        # each line is of form [20,22,24}
        for line in file:
            # strip out leading [
            line = line.lstrip("[")
            # get rid of ending ]
            line = line.rstrip("]\n")
          
            # make a list of the numbers as strings
            text_list = line.split(",")
            temp = list()
            for string in text_list:
                temp.append(int(string))
                
            self.plate.append(temp)
        
        self.valid = True    
        file.close()   
        return True         
   
    def write(self,filename):
        # write configuration data to disc
        file = open(filename,"w")
        file.write(str(self.worm) + "\n")
        
        for i in range(len(self.plate)):
            file.write(str(self.plate[i])+ "\n")
            
        file.close
    
    def default(self):
        # default is Vertex HV4
        # This is largly for my benefit in testing
        self.worm = 90

        self.plate.append([15,16,17,18,19,20])
        self.plate.append([21,23,27,29,31,33])
        self.plate.append([37,39,41,43,47,49])

class ConfigView(tk.Frame):
    # A view that allows the user to change the configuration data
    def __init__(self,master,data,*args,**kwargs):
        tk.Frame.__init__(self,master,*args,**kwargs)
    
        self.data = data
        
        # create widgets and variables to hold data for them
        self.worm_ratio = tk.StringVar()
        tk.Label(self,text = "Worm ratio ").grid(row = 0,column = 0)
        tk.Entry(self,textvar = self.worm_ratio).grid(row = 0,column = 1)
         
        self.plate_var = list()
        for i in range(MAX_PLATES):
            self.plate_var.append(tk.StringVar())
            tk.Label(self,text = "Plate " + str(i + 1) + " ").grid(row = i + 1, column = 0)
            tk.Entry(self,textvar = self.plate_var[i]).grid(row = i + 1,column = 1)
        
        self.error_message = tk.StringVar()
        tk.Label(self,textvariable = self.error_message).grid(row = MAX_PLATES + 1,column = 0)
        tk.Button(self,text ="Save",command = self.do_save).grid(row = MAX_PLATES + 2,column = 2)
        tk.Button(self,text ="Load HV4 defaults",command = self.do_load).grid(row = MAX_PLATES + 2,column = 0)
        #tk.Button(self,text = "Read",command = self.do_read).grid(row = MAX_PLATES + 3,column = 0)
        
        if data.valid:
            self.update_screen()
            
    def do_save(self):
        error = False
        self.error_message.set("")
        try:
            self.data.worm = int(self.worm_ratio.get())
        except:
            error = True
        
        if error or (self.data.worm == 0):
            self.error_message.set("Worm ratio must be non zero integer")
            return
        
        new_list = list()
        try:
            for i in range(MAX_PLATES):
                temp = self.plate_var[i].get()
                holes_text = temp.split(",")
                if holes_text[0] == "":
                    break
                holes_list = list()
                #print(holes_text)
                for hole in holes_text:
                    holes_list.append(int(hole))
                    i += 1
                new_list.append(holes_list)
        except:
            self.error_message.set("Invalid data - hole counts must be integers sepparated by commas")
            return
        
        self.data.plate = new_list
        self.error_message.set("Configuration saved")                                  
        self.data.write(FILENAME)
        self.update_screen()
        
    def do_load(self):
        self.data.default()
        self.update_screen()
        
    #def do_read(self):
    #    self.data.read(FILENAME)
    #    self.update_screen()
        
    def update_screen(self):
        # Update the screen with the current data values
        self.worm_ratio.set(self.data.worm)
     
        # clear Entry fields
        for i in range(MAX_PLATES):
            self.plate_var[i].set("")
            
        i = 0
        for plate in self.data.plate:
            temp = ""
            first = True
            for item in plate:
                if not first:
                    temp += ","
                temp += str(item)
                first = False               
            self.plate_var[i].set(temp)
            i += 1          

        
class MainView(tk.Frame):
    # This is the main calculate window
    def __init__(self,master,data,*args,**kwargs):
        tk.Frame.__init__(self,master,*args,**kwargs)
        
        self.data = data
        tk.Label(self,text ="Number of teeth").grid(row = 0,column = 0)
        
        self.no_teeth = tk.IntVar()
        entry = tk.Entry(self,textvar = self.no_teeth)
        entry.focus_set()
        entry.grid(row = 0,column = 1)
        # make Enter key act like a Calculate press
        entry.bind('<Key-Return>',self.on_return)
              
        tk.Button(self,text = 'Calculate',command = self.DoCalc).grid(row = 0,column = 2)
       
        self.error_message = tk.StringVar()  
        tk.Label(self,textvariable = self.error_message).grid(row = 1,column = 0)
 
        self.full_turns = tk.StringVar()
        tk.Label(self,textvariable = self.full_turns).grid(row = 2,column = 0)
        
        self.part_turns = tk.StringVar()
        tk.Label(self,textvariable = self.part_turns).grid(row = 3,column = 0)
                     
    def on_return(self,x):
        self.DoCalc()
        
    def DoCalc(self):
        # clear messages
        self.error_message.set("")
        self.full_turns.set("")
        self.part_turns.set("")
        
        try:
            teeth = self.no_teeth.get()
        except:
            self.error_message.set("Number of teeth must be an integer")
            return
        if teeth <= 0:
            self.error_message.set("Number of teeth must be a positive integer")
            return
        
        turns = int(self.data.worm/teeth)
        #print(turns)
        self.full_turns.set(str(turns) + " complete turns")
        
        rem = float(self.data.worm)/teeth - turns
        if rem != 0:
            # we need to do part turns
            (plate,num_holes,count) = self.find_plate(rem)

            # check we got a result
            if plate >= 0:
                # do confidence check
                if abs(self.data.worm - teeth*(turns + float(count)/num_holes)) < TOLERANCE:
                    self.part_turns.set("plus " + str(count) + " on " + str(num_holes) + " ring on plate " + str(plate + 1))
                else:
                    #print("Error ",self.data.worm,teeth*(turns + count/num_holes))
                    self.error_message.set("ERROR - cofidence check failed")
            else:
                self.error_message.set("Could not find a solution")
                self.full_turns.set("")
                
    def find_plate(self,rem):
        # we need to find a plate with the right number of holes

        for plate in range(len(self.data.plate)):
            for holes in range(len(self.data.plate[plate])):
                num_holes = self.data.plate[plate][holes]
                for count in range(1,num_holes):
                    if abs(float(count)/num_holes - rem) < TOLERANCE:
                        return (plate,num_holes,count)
        
        return(-1,0,0)                

class Mainframe(tk.Frame):
    # this class is the main frame window
    # It does not have any widgets but views are loaded selectively
    # on top of it
    def __init__(self,master,*args,**kwargs):
        tk.Frame.__init__(self,master,*args,**kwargs)
        
        data = Data()
        data.read(FILENAME)
        
        self.rowconfigure(0,minsize = FRAME_HEIGHT)
        self.columnconfigure(0,minsize = FRAME_WIDTH)
        self.views = dict()
        self.views['mainview'] = MainView(self,data,width = FRAME_WIDTH, height = FRAME_HEIGHT,bd = 0)
        self.views['configview'] = ConfigView(self,data,width = FRAME_WIDTH,height = FRAME_HEIGHT,bd = 0)
                    
        if data.valid:
            self.currentview = self.views['mainview']
        else:
            self.currentview = self.views['configview']
            
        self.currentview.grid(row = 0,column = 0,sticky = tk.N)
        
    def show_view(self,view):
        # show the required view
        self.currentview.grid_forget()
        self.currentview = self.views[view]
        self.currentview.grid(row = 0,column = 0,sticky = tk.N)
       
class MainWindow(tk.Tk):
    # Main window class - often called root
    # It owns the menu
    def __init__(self):
        tk.Tk.__init__(self)
               
        # set the title bar text
        self.title('Dividing Head App')
      
        # create a menu bar
        mainMenu = tk.Menu(self)
        self.config(menu=mainMenu)
        
        # create a file menu with an exit entry
        fileMenu = tk.Menu(mainMenu)
        fileMenu.add_command(label='Exit',command=self.destroy)
        mainMenu.add_cascade(label='File',menu=fileMenu)

        # create a view menu
        viewMenu = tk.Menu(mainMenu)
        viewMenu.add_command(label = 'Configure',command = lambda: self.show_view('configview'))
        viewMenu.add_command(label = 'Calculate',command = lambda: self.show_view('mainview'))
        mainMenu.add_cascade(label = 'View',menu = viewMenu)
            
        # any main menu should have a help entry
        helpMenu = tk.Menu(mainMenu)
        helpMenu.add_command(label = 'about',command = self.showAbout)
        mainMenu.add_cascade(label = 'Help',menu = helpMenu)
        
        # create and pack a Mainframe window
        self.frame = Mainframe(self)
        self.frame.pack()
        
        # now start
        self.mainloop()
        
    def showAbout(self):
        # show the about box
        msg.showinfo('About', 'A division plate program')
        
    def show_view(self,view):
        # switch to the selected view
        self.frame.show_view(view)
    

            
# create an main window object
# it will run itself
MainWindow()
