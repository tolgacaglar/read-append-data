# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 13:08:54 2017

@author: Tolga
"""

# Form for entering data into the json file

# Dialog box and forms
from tkinter import Tk, Button, Toplevel, Menu, OptionMenu, Entry, DoubleVar, StringVar, Label, W, E
from tkinter.messagebox import showinfo, askyesno
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Date structure 
import datetime
import calendar 

# Creating Random characters 
import string
import random

# Mathematical calculations for growth rate
from pylab import polyfit, log

# JSON data structure
import json

# State class with enumeration
# State.LOAD : for loading a json file and updating the necessary fields
# State.SAVE : for Saving entered values to a given file
from enum import Enum
class State(Enum):
    LOAD=1
    SAVE=2
    
# Widget class with enumeration
# Widget.ENTRY_STR: Enter a string value
# Widget.ENTRY_DBL: Enter a float value
# Widget.OPTIONMENU_STR: Choose one
# Widget.LABEL_DBL:  Calculate the double variable
class Widget(Enum):
    ENTRY_STR=1
    ENTRY_DBL=2
    OPTIONMENU_STR=3
    LABEL_DBL=4
    
# Experiment class with enumeration
# Experiment.GROWTH_CURVE
class Experiment(Enum):
    GROWTH_CURVE=1
    
# Type of addition to medi
    
class AppendForm:
    
        def __init__(self, master):
            # Initial state is SAVE
            self.currentstate = State.SAVE
            
            # Cascaded menubar with
            # File -> Open
            # File -> New
            self.menubar = Menu(root)
            self.filemenu = Menu(self.menubar, tearoff=0)
            self.filemenu.add_command(label="Open", command=self.Open)
            self.filemenu.add_command(label="New", command=self.New)
            self.menubar.add_cascade(label="File", menu=self.filemenu)
            root.config(menu=self.menubar)
            
            # Default experiment is growth curve
            self.experiment = Experiment.GROWTH_CURVE
            
            # Default data size of the time-od pairs
            self.datasz = 5;
            self.maxrow = 17;
            
            self.master = master
            master.title("AppendForm")
   
########################################################################################
################   MUST HAVES FOR THE JSON FIlE... ID number and Date ##################
########################################################################################            
            # ID of the experiment
            # Keep the state of the entry disabled
            # Randomly given from computer.
            # Does not check for collisions, might have more than one
            self.idn = StringVar(master, value = self.id_generator())
            self.idn_entry = Entry(master, textvariable=self.idn, state="readonly")
            self.idn_label = Label(master, text = "ID #")
            
            # Date of the experiment
            # Currently set to string variable, consider giving a drop down menu
            #   and choose a date from a calendar
            self.date = StringVar(master, value = "")
            self.date_entry = Entry(master, textvariable=self.date, state="disabled")
            self.date_entry.bind("<ButtonRelease-1>", self.datepicker)
            self.date_label = Label(master, text="Date")
            
############################################################################################            
            
############################################################################################            
##############  PARAMETERS TO BE USED   ####################################################
############################################################################################
            # Parameter Strings shown in the label:
            #       [0]Zeroth item is the type of the Widget
            #       [1]First item defines if common additive can be used (salt, carbon, nitrogen)
            #       [2]Second item is the text label
            #       [3]Third item is the default value of the widget
            #       Rest of the arguments are the option values from OptionMenu widget
            self.carbon_wdgt = [[Widget.OPTIONMENU_STR, True, "carbon", "Glucose", "Acetate", "Pyruvate"],
                                [Widget.ENTRY_DBL, False, "molarity",   0.0]]
            self.nitrogen_wdgt = [[Widget.OPTIONMENU_STR, True, "nitrogen", "NH4Cl"],
                                  [Widget.ENTRY_DBL, False, "molarity", 0.0]]
            self.salt_wdgt = [[Widget.OPTIONMENU_STR, True, "salt", "NaCl", "SSS"],
                              [Widget.ENTRY_DBL, False, "molarity", 0.0]]
            self.parameters_wdgt = [
                    [Widget.OPTIONMENU_STR, False, "species", "NCM3722", "1A01"], 
                    [Widget.ENTRY_DBL, False, "temperature", 37.0],
                    [Widget.ENTRY_DBL, False, "pH", 7.4],
                    [Widget.OPTIONMENU_STR, False, "medium", "MOPS", "N-C-", "ASW"]]
            
            # Additives
            # Change the available additives using carbon_wdgt
            self.parameters_wdgt.append(self.carbon_wdgt[0])
            self.parameters_wdgt.append(self.carbon_wdgt[1])

            self.parameters_wdgt.append(self.nitrogen_wdgt[0])
            self.parameters_wdgt.append(self.nitrogen_wdgt[1])

            self.parameters_wdgt.append(self.salt_wdgt[0])
            self.parameters_wdgt.append(self.salt_wdgt[1])
            
            self.paramsz = 2+len(self.parameters_wdgt)
            self.parameters = []
            self.widgets = []
            self.labels = []
            self.isvalidated = []
            for ix in range(0,len(self.parameters_wdgt)):
                if self.parameters_wdgt[ix][0] == Widget.OPTIONMENU_STR:
                    self.parameters.append(StringVar(master))
                    self.widgets.append(OptionMenu(master, self.parameters[ix], *self.parameters_wdgt[ix][3:]))
                elif self.parameters_wdgt[ix][0] == Widget.ENTRY_DBL:
                    self.parameters.append(DoubleVar(master))
                    self.widgets.append(Entry(master, textvariable=self.parameters[ix]))
                elif self.parameters_wdgt[ix][0] == Widget.ENTRY_STR:
                    self.parameters.append(StringVar(master))
                    self.widgets.append(Entry(master, textvariable=self.parameters[ix]))
                elif self.parameters_wdgt[ix][0] == Widget.LABEL_DBL:
                    self.parameters.append(DoubleVar(master))
                    self.widgets.append(Label(master, textvariable=self.parameters[ix]))
                self.parameters[ix].set(self.parameters_wdgt[ix][3])
                self.labels.append(Label(master, text=self.parameters_wdgt[ix][2]))
                self.isvalidated.append(False)

            # Submit button is not going to append after accepting growth and R2 values
            self.submit_button = Button(master, text="Submit", command=self.submit)
            self.append_button = Button(master, text = "Append", command=self.append)
            self.next_button = Button(master, text = ">" , command=self.Next)
            self.prev_button = Button(master, text = "<" , command = self.Prev)
            
            # Datas
            self.time_label = Label(master, text = "Time(min)")
            self.time = []
            self.time_entries = []
            self.od_label = Label(master,text= "OD")
            self.od = []
            self.od_entries=[]
            self.add_buttons = []
            self.remove_buttons = []
            for tix in range(0,self.datasz):
                self.time_entries.append(Entry(master))
                self.od_entries.append(Entry(master))
                self.add_buttons.append(Button(master, text = "+", command = lambda lix=tix: self.add_entry(lix)))
                self.remove_buttons.append(Button(master, text = "-", command = lambda lix= tix: self.remove_entry(lix)))
            
            # Set the default value for append_check to false
            self.append_check = False;

###############################################################################
###############  Grid Layout    ###############################################
###############################################################################
            # IDN and Date are must. Keep them at the top left!!
            self.idn_label.grid(row=0, column=0, sticky=W)
            self.idn_entry.grid(row=0,column=1, sticky=W)
            
            self.date_label.grid(row=1, column=0, sticky=W)
            self.date_entry.grid(row=1,column=1, sticky=W)

            # Place the rest of the on the left two columns
            for ix in range(0,len(self.parameters)):
                self.labels[ix].grid(row=2+ix,column=0, sticky=W)
                self.widgets[ix].grid(row=2+ix,column=1, sticky=W+E)

            self.submit_button.grid(row=self.maxrow,column=0, sticky=W+E)
            self.append_button.grid(row=self.maxrow,column=3, sticky=W+E)
            self.prev_button.grid(row=self.maxrow,column=1, sticky=W)
            self.next_button.grid(row=self.maxrow,column=1, sticky=E)

            self.total = 0
            self.entered_number = 0
            
            # Types of different experiments
            # This is the biggest and must expansion if we want to keep all of our data in the same way
            # Currently we have only Experiment.GROWTH_CURVE
            if self.experiment == Experiment.GROWTH_CURVE:
                # Time and OD array
                self.time_label.grid(row=0,column=2,sticky=W+E)
                self.od_label.grid(row=0,column=4,sticky=W+E)
                for tix in range(0,self.datasz):
                    self.time_entries[tix].grid(row=1+tix, column=2, sticky=W+E, padx=10)
                    self.od_entries[tix].grid(row=1+tix, column=3, sticky=W+E, padx=10)
                    self.add_buttons[tix].grid(row=1+tix, column=4, sticky=W+E)
                    self.remove_buttons[tix].grid(row=1+tix,column=5, sticky=W+E)
                                        
                # Growth rate label
                self.growth = DoubleVar(master)
                self.growth_lbl = Label(master, textvariable=self.growth)
                self.growth_text= Label(master,text="lambda")
                self.growth.set(0.0)
                self.growth_text.grid(row=1+self.paramsz, column=0, sticky=W)
                self.growth_lbl.grid(row=1+self.paramsz, column=1, sticky=W+E)
                
                
                # R2 label
                self.r2 = DoubleVar(master)
                self.r2_lbl = Label(master,textvariable=self.r2)
                self.r2_text = Label(master, text="R2")
                self.r2.set(1.0)
                self.r2_text.grid(row=2+self.paramsz, column=0, sticky=W)
                self.r2_lbl.grid(row=2+self.paramsz,column=1,sticky=W+E)

        # Method for submit button
        # Validates the entries, and calculates stuff
        def submit(self):              
            self.append_check = self.validate()
            if self.experiment == Experiment.GROWTH_CURVE:
                self.calculate_growth(0,self.datasz)   
                self.calculate_r2(0,self.datasz)
            
        def append(self):
            if self.append_check:
                measured_data = []
                for ix in range(0,self.datasz):
                    measured_data.append({"time": self.time[ix],
                                          "od": self.od[ix]})
                
                # Data must start with idn and date, donot try to change
                data = [{"idn": self.idn.get(),"date": self.date.get()}]
                commons = [];
                
                # For loop for adding the rest of the parameters
                rix = 0
                while rix < len(self.parameters_wdgt):
                    if self.parameters_wdgt[rix][1]:   # An array of common names, such as different sources of salt, carbon, nitrogen
                        if self.isvalidated[rix]:
                            showinfo(title="!!!ERRROR!!!" , message="Validated entry cannot be common!!")
                        else:
                            commons.append({self.parameters_wdgt[rix][2]: self.parameters[rix].get(), 
                                                                        self.parameters_wdgt[rix+1][2]: self.parameters[rix+1]})
                            rix += 1
                    else:    
                        if self.isvalidated[rix]:
                            data[0][self.parameters_wdgt[rix][2]] = self.parameters[rix]
                        else:
                            data[0][self.parameters_wdgt[rix][2]] = self.parameters[rix].get()
                    rix += 1

                data[0]["additives"] = commons
                data[0]["measurement"] = measured_data
                data[0]["growth"] =[{"rate": self.growth.get(), "r2": self.r2.get()}]
               
    
                # Create a new file?
                newfile = askyesno(title=None, message="Create a new file?")
                if newfile: # Create a new file, or overwrite if necessary
                    print("Creating new file")
                    self.filename = asksaveasfilename(defaultextension=".json", filetypes=(("JSON file", "*.json"), ("All Files", "*.*")))
                    # Add title 
                    print("Printing the title to the file : " + self.filename)
                    with open(self.filename, "w") as outfile:
                        json.dump(data, outfile)
                else:       # Append to a given file
                    # Choose a file
                    self.filename = askopenfilename(defaultextension=".json",  filetypes=(("JSON file", "*.json"), ("All Files", "*.*")))
                    # Check if a file is compatible
                    try:
                        self.olddata = json.load(open(self.filename))
                        self.olddata.append(data[0])
                    except IOError:
                        print("Corrupted .json file :'" + self.filename + "'")
                        
                    with open(self.filename, "w") as outfile:
                        json.dump(self.olddata, outfile)
            else:
                showinfo(title="ERROR!", message="Submit before appending")
        def add_entry(self, idx):
            self.datasz += 1
            print("datasz = " + str(self.datasz) + "\nmaxrow = " + str(self.maxrow) + ", idx = " + str(idx))
            
            # Append time and OD entries
            self.time_entries.insert(idx, Entry(self.master))
            self.od_entries.insert(idx,Entry(self.master))
            self.add_buttons.insert(idx,Button(self.master,text='+', command=lambda lix = idx: self.add_entry(lix)))
            self.remove_buttons.insert(idx,Button(self.master,text='-',command=lambda lix = idx: self.remove_entry(lix)))
            # Layout of time and OD entries
            for tix in range(idx,self.datasz):
                self.time_entries[tix].grid(row=1+tix,column=2,sticky=W+E, padx=10)
                self.od_entries[tix].grid(row=1+tix,column=3,sticky=W+E, padx=10)
                self.add_buttons[tix].configure(text='+', command=lambda lix=tix: self.add_entry(lix))
                self.add_buttons[tix].grid(row=1+tix, column=4, sticky=W+E)
                self.remove_buttons[tix].configure(text='-', command=lambda lix=tix: self.remove_entry(lix))
                self.remove_buttons[tix].grid(row=1+tix,column=5, sticky=W+E)
            
            # Check if submit and append buttons need to be relocated
            # Relocate if necessary
            if self.datasz > self.maxrow-6:
                self.maxrow += 1
            self.submit_button.grid(row=self.maxrow, column=0, sticky=W+E)
            self.append_button.grid(row=self.maxrow, column=3, sticky=W+E)
        def remove_entry(self, idx):
            if (self.datasz> 0):
                self.datasz -= 1
            print("datasz = " + str(self.datasz) + "\nmaxrow = " + str(self.maxrow) + ", idx = " + str(idx))
           
            # remove time and od entries from the grid
            self.time_entries[idx].grid_remove()
            self.time_entries.pop(idx)
            self.od_entries[idx].grid_remove()
            self.od_entries.pop(idx)
            # remove add and remove buttons from the grid
            self.add_buttons[idx].grid_remove()
            self.add_buttons.pop(idx)
            self.remove_buttons[idx].grid_remove()
            self.remove_buttons.pop(idx)

            for tix in range(idx,self.datasz):
                self.time_entries[tix].grid(row=1+tix,column=2,sticky=W+E, padx=10)
                self.od_entries[tix].grid(row=1+tix,column=3,sticky=W+E, padx=10)
                self.add_buttons[tix].configure(text='+', command=lambda lix=tix: self.add_entry(lix))
                self.add_buttons[tix].grid(row=1+tix, column=4, sticky=W+E)
                self.remove_buttons[tix].configure(text='-', command=lambda lix=tix: self.remove_entry(lix))
                self.remove_buttons[tix].grid(row=1+tix,column=5, sticky=W+E)
            
        def validate(self):
            # Check the ID
            try:
                error_msg = "Date must be 'YYYY-MM-DD' format"
                datetime.datetime.strptime(self.date.get(), "%Y-%m-%d")

                for ix in range(0,len(self.parameters_wdgt)):
                    if self.parameters_wdgt[ix][0] == Widget.ENTRY_DBL:
                        error_msg = self.parameters_wdgt[ix][2] + " must be a float"
                        self.parameters[ix] = float(self.widgets[ix].get())
                        self.isvalidated[ix] = True
                
                error_msg = "time and OD values must be a float"
                
                if len(self.time) == self.datasz:
                    self.time.clear
                    self.time = []
                    self.od.clear
                    self.od = []
                for ix in range(self.datasz):
                    self.time.append(float(self.time_entries[ix].get()))
                    self.od.append(float(self.od_entries[ix].get()))
                    print("\n[ " + self.time_entries[ix].get() + ", " + self.od_entries[ix].get() + "]")
                    

            except ValueError:
                showinfo(title="ERROR!", message=error_msg)
                return False
            
            return True
        
        def id_generator(self, strsize=8, chars=(string.ascii_uppercase + string.digits)):
            strng = ""
            for ix in range(0,strsize):
                strng += random.choice(chars)
            print(strng)
            return strng
        
        # Calculate growth rate between points 
        def calculate_growth(self, begin, end):
            tvals = []
            odlogvals =[]
            print("time size = " + str(len(self.time)) + ", begin = " + str(begin) + ", end = " + str(end))
            for ix in range(begin,end):
                tvals.append(self.time[ix]/60)
                odlogvals.append(log(self.od[ix]))
                
            rate, b = polyfit(tvals, odlogvals, 1)
            rate = round(rate*100)
            rate /= 100
            self.growth.set(rate)
            self.const = b
            print("rate = " + str(rate) + ", growth_rate = " + str(self.growth.get()))
            
        def calculate_r2(self, begin, end):
            mean = 0.0
            for ix in range(begin,end):
                mean += log(self.od[ix])/(end-begin)
            
            tss = 0.0
            rss = 0.0
            for ix in range(begin,end):
                tss += (self.od[ix]-mean)**2
                rss += (self.const + self.growth.get()*self.time[ix]/60 - mean)**2
            
            r2 = round((1-rss/tss)*100)/100
            self.r2.set(r2)
            
            print("r2 = " + str(self.r2.get()))
            
        def Open(self):
            self.filename = askopenfilename(defaultextension=".json",  filetypes=(("JSON file", "*.json"), ("All Files", "*.*")))
            try:
                self.olddata = json.load(open(self.filename))
                sz = len(self.olddata[0])
                showinfo(title="Warning", message=str(sz) + " experiments are found. Go to desired experiment with > or < buttons")
                self.currentstate = State.LOAD
                self.Update()
            except IOError:
                print("Corrupted file!" + self.filename)
        def New(self):
            keepdata = askyesno(title="Reset", message="Keep the experiment?")
            # Keep all the data except the ID.
            # ID must be different for each measurement, to differentiate different experiments
            self.idn.set(self.id_generator())
            if not keepdata:
                print("Reset all the values")
            self.currentstate = State.SAVE
            self.Update()
        def Update(self):
            print("update")
        def Next(self):
            if self.currentstate == State.LOAD:
                print("find and show next item from data")
            else:
                showinfo(title="Error", message = "Load a file before using the next button")
        def Prev(self):
            if self.currentstate == State.LOAD:
                print("find and show previous item from data")
            else:
                showinfo(title="Error", message = "Load a file before using the previous button")
                
        def datepicker(self, event):
            child = Toplevel()
            Calendar(child, self.date_entry, self.date)
 
####################################################################################
# Calendar class for date picker              ######################################
####################################################################################
class Calendar:
    def __init__(self, parent, wdgt, values):
        self.wdgt = wdgt
        self.values = values
        self.parent = parent
        self.cal = calendar.TextCalendar(calendar.SUNDAY)
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.wid = []
        self.day_selected = 1
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = ''
         
        self.setup(self.year, self.month)
         
    def clear(self):
        for w in self.wid[:]:
            w.grid_forget()
            #w.destroy()
            self.wid.remove(w)
     
    def go_prev(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        #self.selected = (self.month, self.year)
        self.clear()
        self.setup(self.year, self.month)
 
    def go_next(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
         
        #self.selected = (self.month, self.year)
        self.clear()
        self.setup(self.year, self.month)
         
    def selection(self, day, name):
        self.day_selected = day
        self.month_selected = self.month
        self.year_selected = self.year
        self.day_name = name
         
        #data
        self.values.set("%04d-%02d-%02d" % (self.year , self.month , day))
#        self.values['day_selected'] = day
#        self.values['month_selected'] = self.month
#        self.values['year_selected'] = self.year
#        self.values['day_name'] = name
#        self.values['month_name'] = calendar.month_name[self.month_selected]
         
        self.clear()
        self.setup(self.year, self.month)
         
    def setup(self, y, m):
        left = Button(self.parent, text='<', command=self.go_prev)
        self.wid.append(left)
        left.grid(row=0, column=1)
         
        header = Label(self.parent, height=2, text='{}   {}'.format(calendar.month_abbr[m], str(y)))
        self.wid.append(header)
        header.grid(row=0, column=2, columnspan=3)
         
        right = Button(self.parent, text='>', command=self.go_next)
        self.wid.append(right)
        right.grid(row=0, column=5)
         
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for num, name in enumerate(days):
            t = Label(self.parent, text=name[:3])
            self.wid.append(t)
            t.grid(row=1, column=num)
         
        for w, week in enumerate(self.cal.monthdayscalendar(y, m), 2):
            for d, day in enumerate(week):
                if day:
                    #print(calendar.day_name[day])
                    b = Button(self.parent, width=1, text=day, command=lambda day=day:self.selection(day, calendar.day_name[(day-1) % 7]))
                    self.wid.append(b)
                    b.grid(row=w, column=d)
                     
        sel = Label(self.parent, height=2, text='{} {} {} {}'.format(
            self.day_name, calendar.month_name[self.month_selected], self.day_selected, self.year_selected))
        self.wid.append(sel)
        sel.grid(row=8, column=0, columnspan=7)
         
        ok = Button(self.parent, width=5, text='OK', command=self.kill_and_save)
        self.wid.append(ok)
        ok.grid(row=9, column=2, columnspan=3, pady=10)
         
    def kill_and_save(self):
        self.parent.destroy()

            
root = Tk()
app = AppendForm(master=root)
root.mainloop()
