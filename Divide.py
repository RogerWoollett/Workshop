import tkinter as tk
import tkinter.messagebox as msg

FRAME_WIDTH = 400
FRAME_HEIGHT = 200
# used to avoid rounding errors
TOLERANCE = 0.000000001

class Data:
    pass

class MainView(tk.Frame):
    def __init__(self,master,*args,**kwargs):
        tk.Frame.__init__(self,master,*args,**kwargs)
        
        self.data = Data()
        
        # change this to your worm ratio
        self.data.worm = 90
        self.data.plate = list()
        # change this to correspond to the holes in your plates
        # you can add or delete lines as required
        self.data.plate.append([15,16,17,18,19,20])
        self.data.plate.append([21,23,27,29,31,33])
        self.data.plate.append([37,39,41,43,47,49])
 
        tk.Label(self,text ="Number of teeth").grid(row = 0,column = 0)
        
        self.no_teeth = tk.IntVar()
        entry = tk.Entry(self,textvar = self.no_teeth)
        entry.focus_set()
        entry.grid(row = 0,column = 1)
        
        tk.Button(self,text = 'Calculate',command = self.DoCalc).grid(row = 0,column = 2)
       
        self.error_message = tk.StringVar()  
        tk.Label(self,textvariable = self.error_message).grid(row = 1,column = 0)
 
        self.full_turns = tk.StringVar()
        tk.Label(self,textvariable = self.full_turns).grid(row = 2,column = 0)
        
        self.part_turns = tk.StringVar()
        tk.Label(self,textvariable = self.part_turns).grid(row = 3,column = 0)
                     
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
        
        turns = int(self.data.worm/teeth)
        #print(turns)
        self.full_turns.set(str(turns) + " complete turns")
        
        rem = self.data.worm/teeth - turns
        if rem != 0:
            # we need to do part turns
            (plate,num_holes,count) = self.find_plate(rem)

            # check we got a result
            if plate >= 0:
                # do confidence check
                if abs(self.data.worm - teeth*(turns + count/num_holes)) < TOLERANCE:
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
                    if abs(count/num_holes - rem) < TOLERANCE:
                        return (plate,num_holes,count)
        
        return(-1,0,0)                

class Mainframe(tk.Frame):
    
    def __init__(self,master,*args,**kwargs):
        # initialise base class
        tk.Frame.__init__(self,master,*args,**kwargs)
        
        self.rowconfigure(0,minsize = FRAME_HEIGHT)
        self.columnconfigure(0,minsize = FRAME_WIDTH)
        self.views = dict()
        self.views['mainview'] = MainView(self,width = FRAME_WIDTH, height = FRAME_HEIGHT,bd = 0)
        #self.views['cpuview'] = CpuView(self,width = FRAME_WIDTH,height = FRAME_HEIGHT,bd = 0)
        #self.views['memview'] = MemView(self,width = FRAME_WIDTH,height = FRAME_HEIGHT,bd = 0)
                    
        self.currentview = self.views['mainview']
        self.currentview.grid(row = 0,column = 0,sticky = tk.N)
        
    def show_view(self,view):
        self.currentview.stop()
        self.currentview.grid_forget()
        self.currentview = self.views[view]
        self.currentview.grid(row = 0,column = 0,sticky = tk.N)
        self.currentview.start()

class MainWindow(tk.Tk):
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
        
        # any main menu should have a help entry
        helpMenu = tk.Menu(mainMenu)
        helpMenu.add_command(label = 'about',command = self.showAbout)
        mainMenu.add_cascade(label = 'Help',menu = helpMenu)
        
        # create and pack a Mainframe window
        Mainframe(self).pack()
        
        # now start
        self.mainloop()
        
    def showAbout(self):
        # show the about box
        msg.showinfo('About', 'A division plate program')
            
# create an main window object
# it will run itself
MainWindow()
