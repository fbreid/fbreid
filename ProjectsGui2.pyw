#!/usr/bin/python3

import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from os import listdir
from os.path import isfile, join
import datetime
from datetime import date
import string
import re

#set up global variables and default paths to directories
project_dir = os.path.join(os.path.sep, 'Users','fbrei','fbdata','logfile','CurrentProjects') 
log_dir = os.path.join(project_dir,'LogFiles')
comp_dir = os.path.join(project_dir,'Completed')
search_dir = os.path.join(project_dir,'Search')
TODO_dir = os.path.join(project_dir,'TODO')
cur_dir = project_dir
dquote = '"'
squote = "'"
pdict = {}                          #dictionary for priority:name
tdict = {}                          #dictionary for todo list
number = []                         #list to ID new project numbers
datelist = []                       #list with current date values 
todaysdate = str(date.today())
datelist = todaysdate.split("-")
datestring = datelist[1]+datelist[2]+datelist[0]
statuslist = ['Active', 'Inactive']
prioritylist = ['0','1','2','3','4','5','6','7','8','9']

#initialize current year fileprefix.
currentyear = '2019_'
#yearlist = ['2016_','2017_','2018_','2019_','2020_','2021_','2022_']

#Search dialog box

class SearchWin(Frame):

   def __init__(self,parent):
      super().__init__()
      self.win = Toplevel(parent)
      self.win.title("Search")
      self.var_1 = StringVar()   #search string
      self.var_2 = IntVar()   #for case sensitive
      self.var_3 = IntVar()   #include completed files
      self.var_2.set(1)       #default is not case sensitive
      self.var_3.set(0)       #default is don't include completed files
      
      #set up label
      self.label1 = Label(self.win, text="Find", justify=RIGHT)
      self.label1.grid(row=0,column=0,pady=5,sticky=W)

      #set up entery window
      self.entry1 = Entry(self.win, textvariable = self.var_1)
      self.entry1.grid(row=0,column=1,padx=3,pady=4)
      self.entry1.focus_set()
      self.entry1.bind('<Return>',self.doSearch)

      #set up checkbox
      self.cbox = Checkbutton(self.win, text="Case Sensitive", variable = self.var_2)
      self.cbox.grid(row=1,column=1,padx=3,pady=4, sticky=W)
      self.cbox = Checkbutton(self.win, text="Include completed", variable = self.var_3)
      self.cbox.grid(row=2,column=1,padx=3,pady=4, sticky=W)
      

      #set up search button
      self.sbutton = Button(self.win, text="Search", command=self.doSearch)
      self.sbutton.grid(row=3, column=1)
     
#Functions-----------------------------------------------------------------
      
   #carry out the search
   def doSearch(self, _event=None):
      casesensitive = self.var_2.get()
      includecompleted = self.var_3.get()
      searchstring = self.var_1.get()
      if searchstring == '':
         self.win.destroy()
      else:
         strupper = searchstring.upper()     #for replacement in results
         founddict = {}  #dict of name+record number, found text (record)
         recorddict = {} #dict of record number, text list (from file)
         filerecord = [] #list for file lines
         flist = my_gui.getFilePaths(project_dir) #get all project
         if includecompleted:
            compfiles = my_gui.getFilePaths(comp_dir) #all projects in comp
            flist = flist + compfiles    #combined file list    
         #stepwise procedure for getting found dictionary from a file
         for longname in flist:           #for each file in directory   
            filename = os.path.basename(longname) #get record from file
            recorddict = self.getRecordDict(longname) #get dict from record
            for k in recorddict:             #for each record in recorddict
               key = filename + ", record: " + k #make new key
               founddict[key] = []           #assign key to list
               templist = recorddict[k]      #get list from recorddict
               for item in templist:         #check each item
                  if casesensitive == 0:
                     tempitem = item.upper()
                     if strupper in tempitem:
                        item = item.replace(searchstring,"["+strupper+"]")
                        founddict[key].append(item)
                  elif searchstring in item:   #if search string found
                     #now fix the string to indicate what is found
                     item = item.replace(searchstring,"["+strupper+"]")
                     founddict[key].append(item) #add to list for key
               if len(founddict[key]) == 0:  #if list is empty for key
                  del founddict[key]         #delete key
         #write results
         if founddict:
            resfilename = self.writeResultsFile(founddict, searchstring)
            self.openResultsFile(resfilename) 
      self.win.destroy()       
               
   #write results file
   def writeResultsFile(self, founddict, searchstr):
      ct = 0
      date = str(datetime.date.today())
      dlist = date.split("-")
      dt = datetime.datetime.now()          
      datestring = searchstr+" "+dlist[1]+dlist[2]+dlist[0]+"_"+str(dt.hour)+"_"+str(dt.minute)+".txt"
      fname = os.path.join(search_dir, datestring)
      strupper = searchstr.upper()
      with open(fname,'w') as tfh:
         #remember, no returns for text strings in founddict!
         tfh.write("SEARCH RESULTS " +datestring[:-4]+ " FOR: " + strupper + "\n\n")
         for kval in sorted(founddict):
            tfh.write(kval + "\n")   
            tlist = founddict[kval]
            for item in tlist:
               ct = ct + 1
               tfh.write(str(ct) + ".\t" + item+"\n")
            ct = 0
            tfh.write("\n\n")  #separate records
      return fname

   #open gvim window with results
   def openResultsFile(self, resfilename):
      command = "gvim " + dquote+resfilename+dquote + " &"
      if os.path.isfile(resfilename):
         try:
            os.system(command)
         except:
            messagebox.showerror("Error", "File not opended by gvim")
             
   #get a dictionary from a file 
   def getRecordDict(self, longfilename):
      recordlist = []                     #list for records from file
      recorddict = {}                     #empty key, list dictionary
      linecounter = 0                     #counter for lines
      filerecord = self.getFileRecord(longfilename) #list from file
      length = len(filerecord)
      while linecounter < length:
         line=filerecord[linecounter]
         linecounter = linecounter + 1
         if len(line) > 8:
            if line[:8].isdigit() and line[8] == '.':
               key = line[:8]
               while line:
                  recordlist.append(line)
                  if linecounter >= length:
                     break
                  line = filerecord[linecounter]
                  linecounter = linecounter + 1
                  #if not line:
                  #   break
               if key not in recorddict:
                  recorddict[key] = []    #establish new key to list item
                  for item in recordlist: #for each record in recordilst
                     recorddict[key].append(item) #add to key list
                  recordlist.clear()      #clear temp recordlist
      return recorddict                   #return key, list dictionary 

   #get a linelist from a file NEED TO DEAL WITH FILE ERROR/EXCEPTIONS
   def getFileRecord(self, longfilename):
      filerecord = []
      counter = 0
      with open(longfilename, 'r') as tfh:
         for line in tfh:
            counter = counter + 1
            line = line.rstrip()
            filerecord.append(line)
      return filerecord            
       
   #print listst to file with filname having search string, date
   def printFound(self,currlist, complist, searchstr):         
      date = datetime.date.today()
      dt = datetime.datetime.now()          
      title = searchstr+" "+str(date)+" "+str(dt.hour)+"_"+str(dt.minute)+".txt"
      filepath = os.path.join(search_dir,title)
      with open(filepath, 'w') as fh:
         if currlist:
            fh.write("\nFound in CurrentProjects directory (active and inactive):\n\n")
            for item in currlist:
               fh.write(item + "\n")
         if complist:
            fh.write("Items found in Completed directory:\n\n")
            for item in complist:
               fh.write(item + "\n")
      self.editFound(filepath)

   #open a gvim window with search results
   def editFound(self,filepath):
         fcommand = "gvim " + dquote+filepath +dquote + "&"
         if os.path.isfile(filepath):
            try:
               os.system(fcommand)
            except:
               messagebox.showerror("Error", "File not opended by gvim")

   #find all incidences of a string a file      
   def CheckForString1(self,path_name, name_of_file, str_to_find, boolval):
      #returns list with: filename, linenumber, line in file. string     
      if not boolval:
         str_to_find = str_to_find.lower()  #convert for case insensitive
      foundlist = []                        #list for found lines
      lineno = 0                            #record line number
      fpath = os.path.join(path_name, name_of_file)  #set path
      if os.path.isfile(fpath):             #check file
         with open(fpath,'r') as tfile:     #open and close
            for line in tfile:              #scroll each line
               lineno = lineno + 1          #advance line number
               if not boolval:      
                  myline=line.lower()         #convert for case insensitive
               else:
                  myline = line
               if str_to_find in myline:      #if found format for return
                  replacement = "[" + str_to_find.upper() + "]"
                  fixedline = line.replace(str_to_find,replacement)
                  formattedline = name_of_file + ", (Line no. " + str(lineno) + "): " + fixedline 
                  foundlist.append(formattedline)  #add to list
      return foundlist                      #return list

#NEW Project setup window -------------------------------------------------
class NewFileWin(Frame):
 
   def __init__(self, parent):
      super().__init__()
      self.win = Toplevel(parent)
      self.win.title("New File Data")
      self.var_1 = StringVar()
      self.proj_number_str = self.getProjectNumber()
      labelstr = "Project Number: " + self.proj_number_str
      self.var_1.set(labelstr)
      self.var_2 = StringVar()
      self.var_2.set(statuslist[0])
      self.var_3 = StringVar()
      self.var_3.set(prioritylist[1])  #initialize to priority 1
      
      #set up labels and project number inactive Entry
      self.label = Entry(self.win, textvariable=self.var_1,state="readonly",justify = CENTER, relief=FLAT)   #list box label at top 
      self.label.grid(row=0,column=1,pady=5,sticky=S)
      self.label1 = Label(self.win, text="Title:", justify = RIGHT)
      self.label1.grid(row=1,column=0)
      self.label2 = Label(self.win, text="Status:", justify = RIGHT)
      self.label2.grid(row=2,column=0)
      self.label3 = Label(self.win, text="Priority", justify = RIGHT)
      self.label3.grid(row=3,column=0)
      self.label4 = Label(self.win, text="Start:", justify = RIGHT)
      self.label4.grid(row=4,column=0)
      self.label5 = Label(self.win, text="End:", justify = RIGHT)
      self.label5.grid(row=5,column=0)

      #set up entry windows
      self.entry1 = Entry(self.win)
      self.entry1.grid(row=1,column=1, padx = 3,pady=4)
      self.entry1.focus_set()
      self.entry2 = OptionMenu(self.win, self.var_2, *statuslist)
      self.entry2.grid(row=2,column=1, padx = 3, pady=4, sticky=W+E)
      self.entry3 = OptionMenu(self.win, self.var_3, *prioritylist)
      self.entry3.grid(row=3, column=1, padx = 3, pady = 4, sticky=W+E)
      self.entry4 = Entry(self.win)
      self.entry4.grid(row=4,column=1, padx = 3, pady = 4)
      self.entry4.insert(0,datestring)
      self.entry5 = Entry(self.win)
      self.entry5.grid(row=5,column=1, padx = 3, pady=4)
      self.entry5.insert(0,"MMDDYYYY")
            
      #set up button
      self.Cancelbutton = Button(self.win, text="Cancel", command=self.win.destroy)
      self.Cancelbutton.grid(row=4, column=2, padx = 3)
      
      self.OKbutton = Button(self.win, text="Create", command=self.create)
      self.OKbutton.grid(row=3,column=2, padx = 3)
   
   #process create new project button
   def create(self):
      number = self.getProjectNumber()
      title = self.entry1.get()
      if title == "":
         messagebox.showerror("Error","Please add a title")   
      else:
         status = self.var_2.get()
         priority = self.var_3.get()
         start = self.entry4.get()
         end = self.entry5.get()
         projname = os.path.join(project_dir,(number + " " +title))  #path to file

         with open(projname, 'w') as nfh:
            nfh.write("Project: " + number + "\n")
            nfh.write("Title: " + title + "\n")
            nfh.write("Status: " + status + "\n")
            nfh.write("Priority: " + priority + "\n")
            nfh.write("Start: " + start + "\n")
            nfh.write("End: "+ end + "\n")
            nfh.write("Summary:" + "\n")
            nfh.write("Files:\n\n")
            nfh.write("Log:\n\n")
            nfh.write(start + ". " + "Project initiated")
         nfh.close()
         self.win.destroy()
  
   #get new project number 
   def getProjectNumber(self):
      number.clear()
      largest = 0
      files = my_gui.getFiles(project_dir)
      for item in files:
         fname = os.path.join(project_dir,item)
         if os.path.isfile(fname):
             with open(fname,'r') as fh:
               line = fh.readline()
               if currentyear in line:
                  temp = line.split('_')
                  number.append(int(temp[1]))
      files = my_gui.getFiles(comp_dir)
      for item in files:
         fname = os.path.join(comp_dir,item)
         if os.path.isfile(fname):
             with open(fname,'r') as fh:
               line = fh.readline()
               if currentyear in line:
                  temp = line.split('_')
                  number.append(int(temp[1]))
      if number:   #make sure list has numbers in it
         largest=max(number)
      value = largest + 1
      strval = str(value)
      strval = currentyear + strval
      return strval 
      
#------------------------------------------------------------------- 
class MainWindow(Frame):

   def __init__(self, master):
      super().__init__()               #initialize frame class
      self.var_1 = StringVar()         #sets up label with directory
      self.var_2 = StringVar()         #sets up label with list type
      self.setProjectDir(project_dir)  #sets all directory variables
      self.setProjectType(1)           #sets type based on radio buttons
      self.master.title("Projects")    #window title

      #accellerators  
      master.bind('<Control-t>', self.getTODOfile)
      master.bind('<Control-l>', self.openLogFile)
      master.bind('<Control-p>', self.printLog)
      master.bind('<Control-s>', self.search)
      master.bind('<Control-q>', self.quitfunc)
      master.bind('<Control-n>', self.getNewFile)
      master.bind('<Control-o>', self.openActive)

      #create menu instance
      self.menubar = Menu(self.master)
      self.master.config(menu=self.menubar)
      
      #create project menu object
      self.filemenu = Menu(self.menubar,  tearoff=0)
      self.filemenu.add_command(label="Select Project Directory", command=self.getProjectDir)
      self.filemenu.add_separator()
      self.filemenu.add_command(label="TODO List",command=self.getTODOfile,accelerator="Ctrl-t")
      self.filemenu.add_command(label="Open Logfile",command=self.openLogFile, accelerator="Ctrl-l")
      self.filemenu.add_command(label="Print Logfile",command=self.printLog, accelerator="Ctrl-p")
      self.filemenu.add_command(label="Search",command=self.search, accelerator = "Ctrl-s")
      self.filemenu.add_separator()
      self.filemenu.add_command(label="Quit", command=self.master.quit, accelerator = "Ctrl-q")  
      self.menubar.add_cascade(label="Project", menu=self.filemenu)
        
      #create labels
      self.dirlabel = ttk.Entry(self.master, textvariable=self.var_1,state="readonly")   #directory label at bottom
      self.dirlabel.grid(row=7,column=0,columnspan=5,sticky=E+W,padx=3) 
            
      self.label1 = Entry(self.master, textvariable=self.var_2,state="readonly",justify = CENTER, relief=FLAT)   #list box label at top 
      self.label1.grid(row=0,column=1,pady=5,sticky=S)
      
      #create and position scrollbar
      self.scroll1=ttk.Scrollbar(self.master)  #listboxleft
      self.scroll1.grid(column=3,row=1,rowspan=4,pady=4,sticky=W+N+S)

      self.scroll2=ttk.Scrollbar(self.master, orient="horizontal")  #listbox bottom
      self.scroll2.grid(column=0,row=5,columnspan=3,pady=4,sticky=W+E)


      #create listboxes and link scrollbars
      self.listbox = Listbox(self.master, selectmode=EXTENDED)
      self.listbox.grid(sticky=N+E+W,row=1,column=0, rowspan=4, columnspan=3,pady=3,padx=3)
      self.scroll1['command'] = self.listbox.yview
      self.listbox['yscrollcommand'] = self.scroll1.set
      self.scroll2['command'] = self.listbox.xview
      self.listbox['xscrollcommand'] = self.scroll2.set
      self.listbox.bind('<Button-3>',self.getActiveSel)
      self.listbox.bind('<Double-Button-1>',self.getActiveSel)
      #self.listbox.bind('<FocusOut>',lambda clearsel: self.listbox.selection_clear(0,END))

      #create radio buttons
      self.active_button = Radiobutton(self.master, text="Active", variable = self.var_2, value = "Active Projects", command=self.setListbox )
      self.active_button.grid(column=0,row=6,padx=3)      

      self.active_button = Radiobutton(self.master, text="Inactive", variable = self.var_2, value = "Inactive Projects",command=self.setListbox)
      self.active_button.grid(column=1,row=6,padx=3)  
      
      self.active_button = Radiobutton(self.master, text="Completed", variable = self.var_2, value ="Completed Projects",command=self.setListbox)
      self.active_button.grid(column=2,row=6,padx=3)  
                   
      #create buttons (bottom up)
      self.button1 = Button(self.master, text="Ouit",command=self.master.  quit,relief=RAISED,height=1,width=6,bd=2)
      self.button1.grid(row=4,column=4,sticky=N+W,padx=3,pady=3)      

      self.button2 = Button(self.master, text="New",command=self.getNewFile,relief=RAISED,height=1,width=6,bd=2)
      self.button2.grid(row=3,column=4,sticky=N+W,padx=3,pady=3)

      self.button3 = Button(self.master, text="Active",command=self.openActive,relief=RAISED,height=1,width=6,bd=2)
      self.button3.grid(row=2,column=4,sticky=N+W,padx=3,pady=3)

      self.button4 = Button(self.master, text="Log",command=self.openLogFile,relief=RAISED,height=1,width=6,bd=2)
      self.button4.grid(row=1,column=4,sticky=N+W,padx=3,pady=3)
            
      #initialize list boxes
      self.setListbox()


#functions---------------------------------------------------------------

   def quitfunc(self,_event=None):
      self.master.quit()
   
   #make an new project file      
   def getNewFile(self,event=None):      
      win = NewFileWin(self.master)  #open entry dialog for project data

   def search(self,_event=None):
      swin = SearchWin(self.master)
      
   #make and print logfile, saves logfile to log_dir
   def printLog(self, _event=None):
      logfile = self.getLogFile()
      commandstr = "fold -s " + logfile + " | lpr" #Win Notepad print
      try:
         os.system(commandstr)             #issue command to OS
      except IOError:
         messagebox.showerrer("Error", "Print Error")

   #moves a file to the completed directory (NEEDS TESTING)
   def completed(self,filename):
      compname = os.path.join(comp_dir, filename)
      if os.path.isfile(compname):
         with open(compname,'w') as tfh:
            command = "move"+" "+dquote+compname+dquote
            try:
               os.system(fcommand)
            except:
               messagebox.showerror("Error", "File not moved") 

   #open a gvim window with logfile               
   def openLogFile(self, _event=None):
      logfile = self.getLogFile()
      if os.path.isfile(logfile):
         fcommand = "gvim"+" "+dquote+logfile+dquote + " &"
         try:
            os.system(fcommand)
         except:
            messagebox.showerror("Error", "File not opended by gvim")          
   
   #generates logfile, opens in gvim, and saves it to log_dir
   def getLogFile(self):
      printbool = 0
      inactivelist = []                      #temporary inactive list
      pdict.clear()                          #clear the dictionary
      dirname = self.var_1.get()             #get directory
      files = self.getFiles(dirname)         #get files
      logfilenamestr = str(datetime.date.today()) #get date for filename
      logfilenamestr = logfilenamestr + ".txt"  #assemble filename
      logfile = os.path.join(log_dir, logfilenamestr) #make path
      #scroll through filenames
      for item in files:                     #make dict and inactive list
         status = self.getStatus(item)
         if status == "Active":
            status = self.getStatus(item)
            pval = self.getPriority(item)
            pdict[item] = pval
         elif status == "Inactive":
            inactivelist.append(item)
      with open(logfile,'w') as tfh:
         tfh.write("\nTODO ITEMS IN LAST LOG BY PROJECT PRIORITY\n\n")
         tdict = self.getTODOList()
         for k in sorted(tdict, key = tdict.get):  #print key sorted by val
            tfh.write(str(tdict[k]) + ". " + k + "\n")
         tfh.write("\nLATEST LOG FOR ACTIVE PROJECTS BY PRIORITY\n\n")
         for kname in sorted(pdict, key = pdict.get):
            tfh.write("PROJECT (" + str(pdict[kname]) + "): "+kname+'\n')   
            last = self.getLastLog(kname)
            for eachline in last:      #write every line of last log
               tfh.write(eachline)
            tfh.write('\n')            #leave a space
         tfh.write("\n\nINACTIVE PROJECTS\n\n")
         for inactivename in inactivelist:
            tfh.write(inactivename + "\n")
         tfh.close()       
      return logfile
         
   #gets last date item from each project 
   def getLastLog(self,name_of_file):     #returns last log from file
      lastlog = []                     #string list to hold last long data
      lineno = 0                            #to hold line numbers
      fpath = os.path.join(project_dir,name_of_file) #get path to file
      if os.path.isfile(fpath):
         with open(fpath,'r') as tfile:     #file closes automatically
            for line in tfile:              #for each line 
               temp = line[:7]              #get first 8 chars (0..7)
               if temp.isdigit() and line[8] == '.': #check for digits and .
                  lastone = lineno  #if datestring, save as last one...
               lineno = lineno + 1 #keep checking for more dates next line
            tfile.seek(0)                   #from file begining
            for i in range(lastone-1): #go line by line to 0 to lastone-1
               tfile.__next__()                 #advance file ptr
            for line in tfile:              #from there, read and save
               lastlog.append(line)         #append data to log
      lastlog = [x for x in lastlog if x.strip()] #remove all lines w/o text
      return lastlog                     #return last log

   #open gvim with todo list
   def getTODOfile(self, _event=None):
      tdict = self.getTODOList()
      TODOfilenamestr = str(datetime.date.today()) #get date for filename
      TODOfilenamestr = TODOfilenamestr + ".txt"  #assemble filename
      TODOfile = os.path.join(TODO_dir, TODOfilenamestr) #make path
      with open(TODOfile,'w') as tfh:
         tfh.write("TODO ITEMS BY PROJECT PRIORITY\n\n")
         for k in sorted(tdict, key = tdict.get):  #print key sorted by val
            tfh.write(str(tdict[k]) + ". " + k + "\n")
         tfh.close()
      fcommand = "gvim" + " " +dquote+TODOfile+dquote + " &"
      if os.path.isfile(TODOfile):
         try:
            os.system(fcommand)
         except:
            messagebox.showerror("Error", "File not opended by gvim")
      else:
         messagebox.showerror("Error", "File path incorrect?")


   #generates the todo list and returns text, priority dict
   def getTODOList(self):
      tdict.clear()
      dirname = self.var_1.get()             #get directory
      files = self.getFiles(project_dir)
      for item in files: 
         status = self.getStatus(item)     #look in active projects      
         if status == 'Active':        
            pval = self.getPriority(item)  #get priority value of project
            filelastlog = self.getLastLog(item)  #get last log
            for line in filelastlog:      #check for "TODO_" 
               if "TODO" in line:         #if todo present 
                  line = line.strip()     #remove char return
                  line = line + "\n"      #add one char return
                  replacement = "[TODO]"
                  fixedline = line.replace("TODO",replacement)
                  formatstr = item + "\n" + fixedline #assemble string
                  tdict[formatstr] = pval #add to dictionary
      return tdict
   
   #returns the priority of a project record
   def getPriority(self,name_of_file):  #return the priority of projects
      priority = -1                         #default return val
      fpath = os.path.join(project_dir,name_of_file)  #get file path
      if os.path.isfile(fpath):             #check pathname
         with open(fpath,'r') as tfile:     #open (and close) file
            for line in tfile:              #for each line in file
               temp = line[:9]              #check first word
               if temp == 'Priority:':      #if Priority line
                  priority = int(line[9:])  #get value as integer
                  break                     #stop processing and close file
      return priority                    #return value
         
   #determine status of file: returns "Active", "Inactive" or "Completed" 
   def getStatus(self,name_of_file):              #returns status type
      fpath = os.path.join(project_dir,name_of_file) #get path to file
      statstr = ''                           #empty status string
      if os.path.isfile(fpath):
         with open(fpath,'r') as tfile:      #open then close file 
            for line in tfile:               #for each line
               if line[:7] == 'Status:':     #if starts with "Status"
                  line = line.lower()        #make all text lower case
                  if "inactive" in line:     #check for inactive
                     statstr = 'Inactive'    #check for inactive
                  elif "completed" in line:  #Completed found 
                     statstr = 'Completed'   #set return
                  elif "active" in line:     #Active found
                     statstr = 'Active'      #set rturn
                  else: 
                     statstr = 'Not_Determined'   #oops?
                  break                      #end loop once return set
      return statstr                         #return status

   #opens all active files for editing
   def openActive(self,_event=None):
      files = self.getFiles(project_dir)
      for item in files:
         status = self.getStatus(item)
         if status == "Active":
            self.editItem(item)      

   def getFileRecord(self, longfilename):
      filerecord = []
      counter = 0
      with open(longfilename, 'r') as tfh:
         for line in tfh:
            counter = counter + 1
            line = line.rstrip()
            filerecord.append(line)
      return filerecord  
      
   def getDateString(self):
      date = str(datetime.date.today())
      dlist = date.split("-")
      dt = datetime.datetime.now()          
      datestring = dlist[1]+dlist[2]+dlist[0]
      return datestring      

   #Open a file in gvim
   def editItem(self,item):
      frecord = []
      addbool = False
      global dqouote
      dirname = self.var_1.get()
      status = self.var_2.get()
      fpathname = os.path.join(dirname, item)
      #first open for reading to get file record
      frecord = self.getFileRecord(fpathname)
      while len(frecord[-1]) == 0:
         frecord = frecord[:-1]    #trim extra lines from end
      fcommand = "gvim "+dquote+fpathname+dquote+" &" #default for comp or inactive
      if status == "Active Projects":
         addbool = True 
         fcommand = "gvim "+squote+"+normal G $ i"+squote+" "+dquote+fpathname+dquote+" &"                   
      #then open for writing to add new dateline 
      with open(fpathname, 'w') as tfh:
         for line in frecord:
            tfh.write(line + "\n")
         tfh.write("\n") #trailing extra line
         if addbool:
            datestring = self.getDateString()
            tfh.write(datestring + ". ")
      if os.path.isfile(fpathname):
         try:
            os.system(fcommand)
         except:
            messagebox.showerror("Error", "File not opended by gvim")

   #updates the listboxes and moves any completed projects to comp_dir
   def setListbox(self):
      displaytype = self.var_2.get()
      self.listbox.delete(0,'end')
      files = self.getFiles(project_dir)
      #check for completed files and move if found
      if displaytype == "Active Projects":
         self.var_1.set(project_dir)
         for item in files:
            status = self.getStatus(item)
            if status == "Active":
               self.listbox.insert(END, item)
      elif displaytype == "Inactive Projects":
         self.var_1.set(project_dir)
         for item in files:
            status = self.getStatus(item)
            if status == "Inactive":
               self.listbox.insert(END, item)
      elif displaytype == "Completed Projects":
         self.var_1.set(comp_dir)  #set listing directory display
         #first check project dir files...
         for item in files:  #remember this is the project directory
            status = self.getStatus(item)
            if status == "Completed":  #if completed move to comp dir
               fpath = os.path.join(project_dir,item) #get path to file
               command = "mv " + dquote + fpath + dquote+  " " + comp_dir
               try:
                  os.system(command)
               except:
                  print("Error: file not moved to comp dir")
         #now go to comp dir and list files
         files = self.getFiles(comp_dir)
         for item in files: 
            self.listbox.insert(END,item)
              
   #set project type string
   def setProjectType(self,val):
      if val == 1:
         self.var_2.set("Active Projects")
      elif val == 2:
         self.var_2.set("Inactive Projects")
      elif val == 3:
         self.var_2.set("Completed Projects")
      else:
         self.var_2.set("None")      

   #handle active list selections
   def getActiveSel(self, event):      
      widget = event.widget
      selected = [widget.get(i) for i in widget.curselection()]
      for item in selected:
         self.editItem(item)     
                       
   #get directory dialog and set list boxes with files
   def getProjectDir(self):
      dirname = filedialog.askdirectory(initialdir=project_dir)
      self.setProjectDir(dirname) #set all directory variables
      self.setListbox()  #fill list box with appropriate project files
   
   #set all global variables 
   def setProjectDir(self, directory):
      global project_dir, log_dir, comp_dir, search_dir, TODO_dir
      project_dir = directory       #set global variable
      fcommand = "cd " + project_dir   #system command string
      os.system(fcommand)           #change to project directory
      self.var_1.set(project_dir)   #set var_1 to update window
      log_dir = os.path.join(project_dir,'LogFiles')
      comp_dir = os.path.join(project_dir,'Completed')
      search_dir = os.path.join(project_dir,'Search')
      TODO_dir = os.path.join(project_dir,'TODO')

   #gets project filenames (name, no path) list excluding temp files
   def getFiles(self, mypath):
      files = os.listdir(mypath)       #short filenames (not full path)
      tempfiles = []                   #new save list
      for fname in files:              #for each filename
         lname=os.path.join(os.path.sep, mypath, fname)  #full path
         if os.path.isfile(lname):     #check to see if it is a file
            if ('~' in lname) or ('.swp' in lname): #file but not wanted
               os.unlink(lname)        #clean up directory
            else:
               tempfiles.append(fname)    #save file name
      return tempfiles

   #same as getfiles but returns file with whole path
   def getFilePaths(self, mypath):
      files = os.listdir(mypath)       #short filenames (not full path)
      tempfiles = []                   #new save list
      for fname in files:              #for each filename
         lname=os.path.join(os.path.sep, mypath, fname)  #full path
         if os.path.isfile(lname):     #check to see if it is a file
            if ('~' in lname) or ('.swp' in lname): #file but not wanted
               os.unlink(lname)        #clean up directory
            else:
               tempfiles.append(lname)    #save file name
      return tempfiles
 

   def update(self):
      self.setListbox()

   def poll(self):
      self.update()
      self.after(3000,self.poll)  #allow a few seconds for multiselect


if __name__ == "__main__":
   root = Tk()                         #make Tk object
   root.geometry("470x300")            #set size
   root.resizable(FALSE,FALSE)         #make window fixed size
   my_gui = MainWindow(root)           #make window object
   root.after_idle(my_gui.poll)
   root.mainloop()                     #run event loop

