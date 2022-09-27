from os import name
import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter.font import nametofont
from turtle import width
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from tkinter import *
from tkinter import colorchooser
from Settings import Settings
from numpy.core.fromnumeric import var
import edaqcomm
import time
from threading import Thread
from DataManagement import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class some(Settings):
    def __init__(self):
        self.root = Tk()

        #load default settings
        Settings.__init__(self)
        self.fig = plt.figure()
        

        self.data = DataManager()
        self.settings = Settings()

        #setting up the nescessary base for tkinter
        self.mainNotebook = ttk.Notebook(self.root)
        self.mainNotebook.grid(row=1,column=0,rowspan=13)
        self.GraphFrame = Frame(self.mainNotebook)
        self.NumbersFrame = Frame(self.mainNotebook)

        self.GraphFrame.pack(fill="both",expand=1)
        self.NumbersFrame.pack(fill="both",expand=1)

        self.mainNotebook.add(self.GraphFrame,text="Charts")
        self.mainNotebook.add(self.NumbersFrame,text="Meters")

        self.mainNotebook.grid(row=1,column=0,rowspan=13)

        self.setquantityvars()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.GraphFrame)

        self.canvas.get_tk_widget().grid(row=0,column=0,rowspan=len(self.settings.ShownColumns)-1,sticky="ns")

        #initializing channel subplots and number of pins
        self.displaySubplots()

        
        self.settings.Channel1Typevar.trace("w",self.ManageChannelTypes)
        self.settings.Channel2Typevar.trace("w",self.ManageChannelTypes)
        self.settings.Channel3Typevar.trace("w",self.ManageChannelTypes)

        self.LevelcrossingonA.trace("w",self.ManageLevelCrossingLines)
        self.LevelcrossingonB.trace("w",self.ManageLevelCrossingLines)
        self.LevelcrossingonC.trace("w",self.ManageLevelCrossingLines)

        self.Channel1Quantityvar.trace_variable("w",self.ManageQuantityAndUnit)
        self.Channel2Quantityvar.trace_variable("w",self.ManageQuantityAndUnit)
        self.Channel3Quantityvar.trace_variable("w",self.ManageQuantityAndUnit)

        self.Channel1Unit.trace_variable("w",self.ManageQuantityAndUnit)
        self.Channel2Unit.trace_variable("w",self.ManageQuantityAndUnit)
        self.Channel3Unit.trace_variable("w",self.ManageQuantityAndUnit)

        self.samplingfreqval.trace_variable("w",self.ManageSamplingFreq)
        self.averagingvar.trace_variable("w",self.ManageAveraging)
        self.title.trace_variable("w",self.setlabels)
        self.settings.timeframesecvar.trace_variable("w",self.ManageTimeFrame)
        self.settings.timeframepointsvar.trace_variable("w",self.ManageTimeFrame)


        #trace ylimitvariables
        self.ylimitAbotvar.trace_variable("w",self.ManageYlimits)
        self.ylimitAtopvar.trace_variable("w",self.ManageYlimits)
        self.ylimitBbotvar.trace_variable("w",self.ManageYlimits)
        self.ylimitBtopvar.trace_variable("w",self.ManageYlimits)
        self.ylimitCbotvar.trace_variable("w",self.ManageYlimits)
        self.ylimitCtopvar.trace_variable("w",self.ManageYlimits)

        #trace levelcrossing variables
        self.LevelCrossingLevelAvar.trace_variable("w",self.ManageLevelCrossingVariables)
        self.LevelCrossingLevelBvar.trace_variable("w",self.ManageLevelCrossingVariables)
        self.LevelCrossingLevelCvar.trace_variable("w",self.ManageLevelCrossingVariables)

        self.LevelCrossingHystAvar.trace_variable("w",self.ManageLevelCrossingVariables)
        self.LevelCrossingHystBvar.trace_variable("w",self.ManageLevelCrossingVariables)
        self.LevelCrossingHystCvar.trace_variable("w",self.ManageLevelCrossingVariables)

        self.LevelCrossingObjLenAvar.trace_variable("w",self.ManageLevelCrossingVariables)
        self.LevelCrossingObjLenBvar.trace_variable("w",self.ManageLevelCrossingVariables)
        self.LevelCrossingObjLenCvar.trace_variable("w",self.ManageLevelCrossingVariables)


        #Setting up variables to enable stopping and starting charts
        self.pausepressed = time.time()
        self.startpressed = 0
        self.startedat = 0
        self.alltimepaused = 0
        
        #Helper variables for levelcrossing
        self.LevelCrossingPointsA = [[None,None],[None,None]]
        self.LevelCrossingPointsB = [[None,None],[None,None]]
        self.LevelCrossingPointsC = [[None,None],[None,None]]

        # Time [s]    Period [s]   Speed [m/s]
        
        self.plotdata = np.zeros((self.settings.timeframepoints,4))

        self.port = "/dev/ttyUSB0"
        self.connected = False

        #start the animation
        self.ani = animation.FuncAnimation(self.fig, self.UpdatePlot, interval=5, blit=False, repeat=False)
        self.setuptkinter()

        self.tryConnection()

        #start the Datarequest
        Thread(target=self.UpdateData).start()
        self.root.mainloop()

        

    def setlabels(*args):
        if "A" in args[0].settings.ShownColumns:
            args[0].ax.set_xlabel(args[0].title.get())
            args[0].ax.set_ylabel(args[0].ax1Ylabel)
        if "B" in args[0].settings.ShownColumns:
            args[0].ax2.set_xlabel(args[0].title.get())
            args[0].ax2.set_ylabel(args[0].ax2Ylabel)
        if "C" in args[0].settings.ShownColumns:
            args[0].ax3.set_xlabel(args[0].title.get())
            args[0].ax3.set_ylabel(args[0].ax3Ylabel)



    def ManageSamplingFreq(*args):
        try:
            args[0].settings.samplingfreq = float(args[0].samplingfreqval.get())
        except:
            pass

    def ManageTimeFrame(*args):
        if args[1] == "Seconds":
            try:
                args[0].settings.timeframesec = float(args[0].timeframesecvar.get())
                args[0].timeframepointsvar.set(str(args[0].settings.samplingfreq*args[0].settings.timeframesec))
                args[0].settings.timeframepoints = int(round(float(args[0].timeframepointsvar.get())))
            except:
                pass
        elif args[1] == "Points":
            try:
                args[0].settings.timeframepoints = int(round(float(args[0].timeframepointsvar.get())))
                args[0].timeframesecvar.set(str(round((args[0].settings.timeframepoints/args[0].settings.samplingfreq),3)))
                args[0].settings.timeframesec = float(args[0].timeframesecvar.get())
            except:
                pass


    def ManageAveraging(*args):
        try:
            if args[0].averagingvar.get() == "No averaging":
                args[0].settings.averaging = -1
            elif args[0].averagingvar.get() == "4 averages":
                args[0].settings.averaging = 4
            elif args[0].averagingvar.get() == "8 averages":
                args[0].settings.averaging = 8
            elif args[0].averagingvar.get() == "16 averages":
                args[0].settings.averaging = 16

        except:
            pass

    def ManageYlimits(*args):
        if args[1] == "Atop" or args[1] == "Abot":
            try:
                args[0].settings.ylimitAbot = args[0].ylimitAbotvar.get()
                args[0].settings.ylimitAtop = args[0].ylimitAtopvar.get()
            except:
                pass
        if args[1] == "Btop" or args[1] == "Bbot":
            try:
                args[0].settings.ylimitBbot = args[0].ylimitBbotvar.get()
                args[0].settings.ylimitBtop = args[0].ylimitBtopvar.get()
            except:
                pass
        if args[1] == "Ctop" or args[1] == "Cbot":
            try:
                args[0].settings.ylimitCbot = args[0].ylimitCbotvar.get()
                args[0].settings.ylimitCtop = args[0].ylimitCtopvar.get()
            except:
                pass

    def ManageShownChannels(self,subplot):
        self.HideSubplot(subplot)
        '''
        print(self.AisShown,self.AisShown.get())
        print(self.BisShown,self.BisShown.get())
        print(self.CisShown,self.CisShown.get())
        '''
        

    def ManageLevelCrossingVariables(*args):
            if args[1] == "Alevel" or args[1] == "AHyst" or args[1] == "AObjLen":
                try:
                    args[0].settings.LevelCrossingLevelA = args[0].LevelCrossingLevelAvar.get()
                    args[0].settings.LevelCrossingHystA = args[0].settings.LevelCrossingHystAvar.get()
                    args[0].settings.LevelCrossingObjLenA = args[0].LevelCrossingObjLenAvar.get()
                except:
                    pass
            if args[1] == "Blevel" or args[1] == "BHyst" or args[1] == "BObjLen":
                try:
                    args[0].settings.LevelCrossingLevelB = args[0].LevelCrossingLevelBvar.get()
                    args[0].settings.LevelCrossingHystB = args[0].LevelCrossingHystBvar.get()
                    args[0].settings.LevelCrossingObjLenB = args[0].LevelCrossingObjLenBvar.get()
                except:
                    pass
            if args[1] == "Clevel" or args[1] == "CHyst" or args[1] == "CObjLen":
                try:
                    args[0].settings.LevelCrossingLevelC = args[0].LevelCrossingLevelCvar.get()
                    args[0].settings.LevelCrossingHystC = args[0].LevelCrossingHystCvar.get()
                    args[0].settings.LevelCrossingObjLenC = args[0].LevelCrossingObjLenCvar.get()
                except:
                    pass

    def ManageQuantityAndUnit(*args):
        if (args[1] == "Aquantity" or args[1] == "AUnit"):
            if args[0].Channel1LinTherm.get() == "Thermistor":
                if args[0].Channel1Unit.get() == "k" or args[0].Channel1Unit.get() == "K":
                    args[0].Channel1Unit.set("K")
                elif args[0].Channel1Unit.get() == "":
                    pass
                else:
                    args[0].Channel1Unit.set("°C")
                args[0].ax1Ylabel = args[0].Channel1Quantityvar.get() + " [" + args[0].Channel1Unit.get() + "]"
            if args[0].Channel1Quantityvar.get() == "":
                args[0].ax1Ylabel = "U [V]"
            else:
                args[0].ax1Ylabel = args[0].Channel1Quantityvar.get() + " [" + args[0].Channel1Unit.get() + "]"

        if (args[1] == "Bquantity" or args[1] == "BUnit"):
            if args[0].Channel2LinTherm.get() == "Thermistor":
                if args[0].Channel2Unit.get() == "k" or args[0].Channel2Unit.get() == "K":
                    args[0].Channel2Unit.set("K")
                elif args[0].Channel2Unit.get() == "":
                    pass
                else:
                    args[0].Channel2Unit.set("°C")
                args[0].ax2Ylabel = args[0].Channel2Quantityvar.get() + " [" + args[0].Channel2Unit.get() + "]"
            if args[0].Channel2Quantityvar.get() == "":
                args[0].Channel2Quantityvar.set("U")
                args[0].ax2Ylabel = "U [V]"
            else:
                args[0].ax2Ylabel = args[0].Channel2Quantityvar.get() + " [" + args[0].Channel2Unit.get() + "]"

        if (args[1] == "Cquantity" or args[1] == "CUnit"):
            if args[0].Channel3LinTherm.get() == "Thermistor":
                if args[0].Channel3Unit.get() == "k" or args[0].Channel3Unit.get() == "K":
                    args[0].Channel3Unit.set("K")
                elif args[0].Channel3Unit.get() == "":
                    pass
                else:
                    args[0].Channel3Unit.set("°C")
                args[0].ax3Ylabel = args[0].Channel3Quantityvar.get() + " [" + args[0].Channel3Unit.get() + "]"
            if args[0].Channel3Quantityvar.get() == "":
                args[0].Channel3Quantityvar.set("U")
                args[0].ax3Ylabel = "U [V]"
            else:
                args[0].ax3Ylabel = args[0].Channel3Quantityvar.get() + " [" + args[0].Channel3Unit.get() + "]"

        args[0].setlabels()

    def hide_chart(self):
        if self.visible:
            self.visible = False
            self.canvas.get_tk_widget().grid_forget()
        else:
            self.visible = True
            self.canvas.get_tk_widget().grid(row=1,column=0,rowspan=13)


    def stop_charts(self):
        #self.comm.stopContSampling()
        self.pause = True
        self.pausepressed = time.time()
        self.stopbutton['state'] = DISABLED
        self.startbutton['state'] = NORMAL
        self.SaveDataTxtButton['state'] = NORMAL
        self.SaveDataExcelButton['state'] = NORMAL

        self.ConnexionMenu.entryconfig(0,state=NORMAL)
        self.filemenu.entryconfig(1,state=NORMAL)
        self.filemenu.entryconfig(3,state=NORMAL)
        self.filemenu.entryconfig(4,state=NORMAL)
        self.filemenu.entryconfig(5,state=NORMAL)
        self.Chartmenu.entryconfig(2,state=NORMAL)

        self.SetChannelAType.configure(state="normal")
        self.SetChannelBType.configure(state="normal")
        self.SetChannelCType.configure(state="normal")
        
        self.ClearDataButton['state'] = NORMAL

        if self.AWindow != None:
            if tkinter.Toplevel.winfo_exists(self.AWindow):
                self.ChannelALinTherm['state'] = NORMAL
                self.ChannelALinTherm['state'] = NORMAL
                self.EntryChannelAName['state'] = NORMAL
                self.EntryChannelAQuantity['state'] = NORMAL
                self.EntryChannelAUnit['state'] = NORMAL
                self.EditASensorButton['state'] = NORMAL

        if self.BWindow != None:
            if tkinter.Toplevel.winfo_exists(self.BWindow):
                self.ChannelBLinTherm['state'] = NORMAL
                self.ChannelBLinTherm['state'] = NORMAL
                self.EntryChannelBName['state'] = NORMAL
                self.EntryChannelBQuantity['state'] = NORMAL
                self.EntryChannelBUnit['state'] = NORMAL
                self.EditBSensorButton['state'] = NORMAL

        if self.CWindow != None:
            if tkinter.Toplevel.winfo_exists(self.CWindow):
                self.ChannelCLinTherm['state'] = NORMAL
                self.ChannelCLinTherm['state'] = NORMAL
                self.EntryChannelCName['state'] = NORMAL
                self.EntryChannelCQuantity['state'] = NORMAL
                self.EntryChannelCUnit['state'] = NORMAL
                self.EditCSensorButton['state'] = NORMAL


        time.sleep(0.1)
        
    def clear_data(self):
        self.data.clear_data()
        self.startedat = 0
        self.startpressed = 0
        self.pausepressed = 0
        self.alltimepaused = 0
        self.plotdata = np.zeros((self.settings.timeframepoints,4))
        self.HystData = {"A":[],"B":[],"C":[]}
        self.LatestHystData = {"A":['','',''],"B":['','',''],"C":['','','']}
        self.HideSubplot(None)

    def start_charts(self):
        #self.comm.startContSampling()
        '''
        print("name ",self.Channel1Name.get())
        print("quantity ",self.settings.Channel1Quantity)
        print("quantityvar ",self.Channel1Quantityvar.get())
        print("unit ",self.Channel1Unit.get())
        print("intercept ",self.settings.Channel1Intercept)
        print("slope ",self.settings.Channel1Slope)
        print("coefficient ",self.settings.Channel1BCoefficient)
        print("reference res ",self.settings.Channel1ReferenceRes)
        print("probe res ",self.settings.Channel1ProbeRes)
        '''



        self.pause = False
        self.startpressed = time.time()
        if self.startedat == 0:
            self.startedat = time.time()
        else:
            self.alltimepaused += self.startpressed-self.pausepressed
        self.startbutton['state'] = DISABLED
        self.stopbutton['state'] = NORMAL
        self.SaveDataTxtButton['state'] = DISABLED
        self.SaveDataExcelButton['state'] = DISABLED

        self.ConnexionMenu.entryconfig(0,state=DISABLED)
        self.filemenu.entryconfig(1,state=DISABLED)
        self.filemenu.entryconfig(3,state=DISABLED)
        self.filemenu.entryconfig(4,state=DISABLED)
        self.filemenu.entryconfig(5,state=DISABLED)
        self.Chartmenu.entryconfig(2,state=DISABLED)

        self.SetChannelAType.configure(state="disabled")
        self.SetChannelCType.configure(state="disabled")
        self.SetChannelBType.configure(state="disabled")
        self.ClearDataButton['state'] = DISABLED
        
        if self.AWindow != None:
            if tkinter.Toplevel.winfo_exists(self.AWindow):
                self.ChannelALinTherm['state'] = DISABLED
                self.EntryChannelAName['state'] = DISABLED
                self.EntryChannelAQuantity['state'] = DISABLED
                self.EntryChannelAUnit['state'] = DISABLED
                self.EditASensorButton['state'] = DISABLED

        if self.BWindow != None:
            if tkinter.Toplevel.winfo_exists(self.BWindow):
                self.ChannelBLinTherm['state'] = DISABLED 
                self.EntryChannelBName['state'] = DISABLED 
                self.EntryChannelBQuantity['state'] = DISABLED 
                self.EntryChannelBUnit['state'] = DISABLED 
                self.EditBSensorButton['state'] = DISABLED 
        
        if self.CWindow != None:
            if tkinter.Toplevel.winfo_exists(self.CWindow):
                self.ChannelCLinTherm['state'] = DISABLED 
                self.EntryChannelCName['state'] = DISABLED 
                self.EntryChannelCQuantity['state'] = DISABLED 
                self.EntryChannelCUnit['state'] = DISABLED 
                self.EditCSensorButton['state'] = DISABLED 

    def start_or_stop_charts(self):
        if self.pause:
            self.start_charts()
        else:
            self.stop_charts()

    def setquantityvars(self):
        if self.Channel1Quantityvar.get() == "":
            self.Channel1Quantityvar.set("U")
        if self.Channel2Quantityvar.get() == "":
            self.Channel2Quantityvar.set("U")
        if self.Channel3Quantityvar.get() == "":
            self.Channel3Quantityvar.set("U")

    def displaySubplots(self):
        NumOfSubplots = len(self.settings.ShownColumns)-1
        self.NumbersFrame.rowconfigure(NumOfSubplots,weight=1)
        self.NumbersFrame.columnconfigure(1,weight=1)       
        currentplot = 0
        if "A" in self.settings.ShownColumns:
            currentplot += 1
            num = 100*NumOfSubplots+10+currentplot
            self.ax = self.fig.add_subplot(num)
            self.ax.locator_params(nbins=self.axNumOfPins)
            self.line,  = self.ax.plot([],[], color=self.settings.line1Color, linestyle="-")         
            self.Alabel = Label(self.NumbersFrame,font=("Trebuchet MS",60),justify=LEFT,anchor="w",width=11,fg=self.line1Color,text="%s = 0 %s" % (self.Channel1Quantityvar.get(),self.Channel1Unit.get()))
            self.Alabel.grid(row=currentplot,column=1,sticky="nsw")
            if self.LevelcrossingonA.get():
                self.linelevelcrossingmin,  = self.ax.plot([],[], color="red", linestyle="-")
                self.linelevelcrossingmax,  = self.ax.plot([],[], color="red", linestyle="-")

        if "B" in self.settings.ShownColumns:
            currentplot += 1
            num = 100*NumOfSubplots+10+currentplot
            self.ax2 = self.fig.add_subplot(num)
            self.ax2.locator_params(nbins=self.ax2NumOfPins)
            self.line2,  = self.ax2.plot([],[], color=self.settings.line2Color, linestyle="-")
            self.Blabel = Label(self.NumbersFrame,justify=LEFT,anchor="w",width=11,font=("Trebuchet MS",60),fg=self.line2Color,text="%s = 0 %s" % (self.Channel2Quantityvar.get(),self.Channel2Unit.get()))
            self.Blabel.grid(row=currentplot,column=1,sticky="nsw")
            if self.LevelcrossingonB.get():
                self.line2levelcrossingmin,  = self.ax2.plot([],[], color="red", linestyle="-")
                self.line2levelcrossingmax,  = self.ax2.plot([],[], color="red", linestyle="-")       

        if "C" in self.settings.ShownColumns:
            currentplot += 1
            num = 100*NumOfSubplots+10+currentplot
            self.ax3 = self.fig.add_subplot(num)
            self.ax3.locator_params(nbins=self.ax3NumOfPins)
            self.line3,  = self.ax3.plot([],[], color=self.settings.line3Color, linestyle="-")        
            self.Clabel = Label(self.NumbersFrame,font=("Trebuchet MS",60),justify=LEFT,anchor="w",width=11,fg=self.line3Color,text="%s = 0 %s" % (self.Channel3Quantityvar.get(),self.Channel3Unit.get()))
            self.Clabel.grid(row=currentplot,column=1,sticky="nsw")
            if self.LevelcrossingonC.get():
                self.line3levelcrossingmin,  = self.ax3.plot([],[], color="red", linestyle="-")
                self.line3levelcrossingmax,  = self.ax3.plot([],[], color="red", linestyle="-")

        self.setlabels()
        if (self.LevelcrossingonA.get() == 1 and "A" in self.settings.ShownColumns) or (self.LevelcrossingonB.get() == 1 and "B" in self.settings.ShownColumns) or (self.LevelcrossingonC.get() == 1 and "C" in self.settings.ShownColumns):
            self.OpenLevelCrossingCharts()
            self.fig.tight_layout()

    def HideSubplot(self,subplot):  
        #delete all subplots from the chart   
        for i in self.fig.get_axes():
            self.fig.delaxes(i)

        #delete all labels from the meters frame
        for i in self.NumbersFrame.winfo_children():
            i.destroy()
        
        #save last rows of the tables
        for i in self.LatestHystData:
            if self.LatestHystData[i] != ['','','']:
                if len(self.HystData[i]) == 0:
                    self.HystData[i].append(list(self.LatestHystData[i]))
                elif self.LatestHystData[i] != self.HystData[i][-1]:
                    self.HystData[i].append(list(self.LatestHystData[i]))
            else:
                pass

        #get rid of elements in graph frame
        for i in self.GraphFrame.winfo_children():
            if type(i) != tkinter.Canvas:
                i.destroy()
            else:
                i.grid_forget()

        

        if subplot in self.settings.ShownColumns:
            #hide plot
            self.settings.ShownColumns.remove(subplot)                       
        elif subplot != None:
            #show subplot
            self.settings.ShownColumns.append(subplot)
        rspan = len(self.settings.ShownColumns)-1
        if rspan == 0:
            rspan += 1
        self.canvas.get_tk_widget().grid(row=0,column=0,rowspan=rspan,sticky="ns")
        self.displaySubplots()
            
        

    def ManageLevelCrossingLines(*args):
        args[0].HideSubplot(None)

    def ChangeLineColor(self,channel):
        color = colorchooser.askcolor()[1]
        if channel == "A":
            self.settings.line1Color = color
            self.ColorA['bg'] = color
        if channel == "B":
            self.settings.line2Color = color
            self.ColorB['bg'] = color
        if channel == "C":
            self.settings.line3Color = color
            self.ColorC['bg'] = color

        self.HideSubplot(None)

    def ClearLcData(self,channel):
        self.HystData[channel] = []
        self.LatestHystData[channel] = ['','','']
        self.HideSubplot(None)

    def CopyLcData(self,channel):
        data = self.HystData[channel]
        data.append(self.LatestHystData[channel])
        df = pd.DataFrame(data,columns=['Time [s]','Period [s]','Speed [m/s]'])
        df.to_clipboard(index=False,header=True)


    def OpenLevelCrossingCharts(self):   
        self.columnwidth = 80 

        self.columns = ('Time [s]','Period [s]','Speed [m/s]')

        nametofont("TkHeadingFont").configure(size=8)

        # define headings
        
        self.tree = ttk.Treeview(self.GraphFrame, columns=self.columns,height=1, show='headings')
        self.tree.heading('Time [s]', text='Time [s]')
        self.tree.heading('Period [s]', text='Period [s]')
        self.tree.heading('Speed [m/s]', text='Speed [m/s]')
        self.tree.column('Time [s]',width=self.columnwidth)
        self.tree.column('Period [s]',width=self.columnwidth)
        self.tree.column('Speed [m/s]',width=self.columnwidth)      
        self.tree.bind("<Button-3>",lambda event: self.LCPopupMenu(event,"A"))

        self.scrollbar = ttk.Scrollbar(self.GraphFrame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        self.tree1 = ttk.Treeview(self.GraphFrame, columns=self.columns,height=1, show='headings')
        self.tree1.heading('Time [s]', text='Time [s]')
        self.tree1.heading('Period [s]', text='Period [s]')
        self.tree1.heading('Speed [m/s]', text='Speed [m/s]')
        self.tree1.column('Time [s]',width=self.columnwidth)
        self.tree1.column('Period [s]',width=self.columnwidth)
        self.tree1.column('Speed [m/s]',width=self.columnwidth)
        self.tree1.bind("<Button-3>",lambda event: self.LCPopupMenu(event,"B"))

        self.scrollbar1 = ttk.Scrollbar(self.GraphFrame, orient=VERTICAL, command=self.tree1.yview)
        self.tree1.configure(yscroll=self.scrollbar1.set)

        self.tree2 = ttk.Treeview(self.GraphFrame, columns=self.columns,height=1, show='headings')
        self.tree2.heading('Time [s]', text='Time [s]')
        self.tree2.heading('Period [s]', text='Period [s]')
        self.tree2.heading('Speed [m/s]', text='Speed [m/s]')
        self.tree2.column('Time [s]',width=self.columnwidth)
        self.tree2.column('Period [s]',width=self.columnwidth)
        self.tree2.column('Speed [m/s]',width=self.columnwidth)
        self.tree2.bind("<Button-3>",lambda event: self.LCPopupMenu(event,"C"))

        self.scrollbar2 = ttk.Scrollbar(self.GraphFrame, orient=VERTICAL, command=self.tree2.yview)
        self.tree2.configure(yscroll=self.scrollbar2.set)

        self.tree.tag_configure('oddrow',background="white")
        self.tree.tag_configure('evenrow',background=self.line1Color)
        self.tree1.tag_configure('oddrow',background="white")
        self.tree1.tag_configure('evenrow',background=self.line2Color)
        self.tree2.tag_configure('oddrow',background="white")
        self.tree2.tag_configure('evenrow',background=self.line3Color)


        curchart = 0
        if "A" in self.settings.ShownColumns: 
            for i in range(len(self.HystData["A"])):
                if i % 2 == 0:
                    self.tree.insert('',END, values=self.HystData["A"][i],tags=('evenrow',))
                else:
                    self.tree.insert('',END, values=self.HystData["A"][i],tags=('oddrow',))
            self.tree.grid(row=curchart, column=1, sticky='nsew')
            self.scrollbar.grid(row=curchart, column=2, sticky='ns')
            if len(self.HystData["A"]) > 0:
                del self.HystData["A"][-1]
            curchart+=1

        if "B" in self.settings.ShownColumns:
            for i in range(len(self.HystData["B"])):
                if i % 2 == 0:
                    self.tree1.insert('',END, values=self.HystData["B"][i],tags=('evenrow',))
                else:
                    self.tree1.insert('',END, values=self.HystData["B"][i],tags=('oddrow',))
            self.tree1.grid(row=curchart, column=1, sticky='nsew')
            self.scrollbar1.grid(row=curchart, column=2, sticky='ns')
            if len(self.HystData["B"]) > 0:
                del self.HystData["B"][-1]
            curchart+=1

        if "C" in self.settings.ShownColumns:
            for i in range(len(self.HystData["C"])):
                if i % 2 == 0:
                    self.tree2.insert('',END, values=self.HystData["C"][i],tags=('evenrow',))
                else:
                    self.tree2.insert('',END, values=self.HystData["C"][i],tags=('oddrow',))
            self.tree2.grid(row=curchart, column=1, sticky='nsew')
            self.scrollbar2.grid(row=curchart, column=2, sticky='ns')
            if len(self.HystData["C"]) > 0:
                del self.HystData["C"][-1]


    def openAWindow(self):
        if self.AWindow == None or not(tkinter.Toplevel.winfo_exists(self.AWindow)):
            self.AWindow = Toplevel(self.root)
            self.AWindow.title("A settings")
            self.HideSubplotA = Button(self.AWindow,text="HideSubplotA",command=lambda: self.HideSubplot("A"))
            self.ColorA = Button(self.AWindow,text="color",bg=self.settings.line1Color,command= lambda: self.ChangeLineColor("A"))
            self.SetChannelAType = OptionMenu(self.AWindow,self.settings.Channel1Typevar,"voltage","resistor","inamp","photo")
            self.ChannelALinTherm = OptionMenu(self.AWindow,self.Channel1LinTherm,"Linear","Thermistor")
            self.EntryChannelAName = Entry(self.AWindow,textvariable=self.Channel1Name)
            self.EntryChannelAQuantity = Entry(self.AWindow,textvariable=self.Channel1Quantityvar)
            self.EntryChannelAUnit = Entry(self.AWindow,textvariable=self.Channel1Unit)
            self.EditASensorButton = Button(self.AWindow,text="Edit sensor",pady=10)       
            self.EntryAylimitBot = Entry(self.AWindow,textvariable=self.ylimitAbotvar)
            self.EntryAylimitTop = Entry(self.AWindow,textvariable=self.ylimitAtopvar)
            self.ChannelAAutoscale = Checkbutton(self.AWindow,text="Autoscale", variable=self.automatic_scaleA)
            self.ChannelALevelcrossing = Checkbutton(self.AWindow,text="Active", variable=self.LevelcrossingonA)
            self.EntryALevelcrossingLevel = Entry(self.AWindow,textvariable=self.LevelCrossingLevelAvar)
            self.EntryALevelcrossingHyst = Entry(self.AWindow,textvariable=self.LevelCrossingHystAvar)
            self.EntryALevelcrossingObjLen = Entry(self.AWindow,textvariable=self.LevelCrossingObjLenAvar)

            Label(self.AWindow,text="Sensor interfacing",pady=10).grid(row=1,column=0,columnspan=2)
            Label(self.AWindow,text="Sensor").grid(row=3,column=0)
            Label(self.AWindow,text="Type").grid(row=4,column=0)
            Label(self.AWindow,text="Name").grid(row=5,column=0)
            Label(self.AWindow,text="Quantity").grid(row=6,column=0)
            Label(self.AWindow,text="Unit").grid(row=7,column=0)
            Label(self.AWindow,text="Reference:").grid(row=8,column=0)
            Label(self.AWindow,text=str(self.settings.Channel1ReferenceRes)+" Ω "+ "at 298,15 K").grid(row=8,column=1)
            Label(self.AWindow,text="Coefficient:").grid(row=9,column=0)
            Label(self.AWindow,text=str(self.settings.Channel1BCoefficient)+"K").grid(row=9,column=1)
            Label(self.AWindow,text="Probe resistance:").grid(row=10,column=0)
            Label(self.AWindow,text=str(self.settings.Channel1ProbeRes)+" Ω").grid(row=10,column=1)
            Label(self.AWindow,text="Chart Y axis").grid(row=12,column=0)
            Label(self.AWindow,text="Minimum").grid(row=13,column=0)
            Label(self.AWindow,text="Maximum").grid(row=16,column=0)
            Label(self.AWindow,text="Level-crossing detector").grid(row=18,column=0)
            Label(self.AWindow,text="Level").grid(row=20,column=0)
            Label(self.AWindow,text="Hysteresis").grid(row=22,column=0)
            Label(self.AWindow,text="Object length [m]").grid(row=24,column=0)

            self.HideSubplotA.grid(row=0,column=0)
            self.ColorA.grid(row=0,column=1)
            self.SetChannelAType.grid(row=2,column=0,columnspan=2)
            self.ChannelALinTherm.grid(row=4,column=1)
            self.EntryChannelAName.grid(row=5,column=1)
            self.EntryChannelAQuantity.grid(row=6,column=1)
            self.EntryChannelAUnit.grid(row=7,column=1)
            self.EditASensorButton.grid(row=11,column=0,columnspan=2)
            self.EntryAylimitBot.grid(row=14,column=0)
            self.ChannelAAutoscale.grid(row=15,column=1)
            self.EntryAylimitTop.grid(row=17,column=0)
            self.ChannelALevelcrossing.grid(row=19,column=0)
            self.EntryALevelcrossingLevel.grid(row=21,column=0)
            self.EntryALevelcrossingHyst.grid(row=23,column=0)
            self.EntryALevelcrossingObjLen.grid(row=25,column=0)

            if not(self.pause):
                self.ChannelALinTherm['state'] = DISABLED
                self.EntryChannelAName['state'] = DISABLED
                self.EntryChannelAQuantity['state'] = DISABLED
                self.EntryChannelAUnit['state'] = DISABLED
                self.EditASensorButton['state'] = DISABLED

    def openBWindow(self):
        if self.BWindow == None or not(tkinter.Toplevel.winfo_exists(self.BWindow)):
            self.BWindow = Toplevel(self.root)
            self.BWindow.title("B settings")
            self.HideSubplotB = Button(self.BWindow,text="HideSubplotB",command=lambda: self.HideSubplot("B"))
            self.ColorB = Button(self.BWindow,text="color",bg=self.settings.line2Color,command= lambda: self.ChangeLineColor("B"))
            self.SetChannelBType = OptionMenu(self.BWindow,self.settings.Channel2Typevar,"voltage","resistor","inamp","photo")
            self.ChannelBLinTherm = OptionMenu(self.BWindow,self.Channel2LinTherm,"Linear","Thermistor")
            self.EntryChannelBName = Entry(self.BWindow,textvariable=self.Channel2Name)
            self.EntryChannelBQuantity = Entry(self.BWindow,textvariable=self.Channel2Quantityvar)
            self.EntryChannelBUnit = Entry(self.BWindow,textvariable=self.Channel2Unit)
            self.EditBSensorButton = Button(self.BWindow,text="Edit sensor",pady=10)       
            self.EntryBylimitBot = Entry(self.BWindow,textvariable=self.ylimitBbotvar)
            self.EntryBylimitTop = Entry(self.BWindow,textvariable=self.ylimitBtopvar)
            self.ChannelBButoscale = Checkbutton(self.BWindow,text="Autoscale", variable=self.automatic_scaleB)
            self.ChannelBLevelcrossing = Checkbutton(self.BWindow,text="Active", variable=self.LevelcrossingonB)
            self.EntryBLevelcrossingLevel = Entry(self.BWindow,textvariable=self.LevelCrossingLevelBvar)
            self.EntryBLevelcrossingHyst = Entry(self.BWindow,textvariable=self.LevelCrossingHystBvar)
            self.EntryBLevelcrossingObjLen = Entry(self.BWindow,textvariable=self.LevelCrossingObjLenBvar)

            Label(self.BWindow,text="Sensor interfacing",pady=10).grid(row=1,column=0,columnspan=2)
            Label(self.BWindow,text="Sensor").grid(row=3,column=0)
            Label(self.BWindow,text="Type").grid(row=4,column=0)
            Label(self.BWindow,text="Name").grid(row=5,column=0)
            Label(self.BWindow,text="Quantity").grid(row=6,column=0)
            Label(self.BWindow,text="Unit").grid(row=7,column=0)
            Label(self.BWindow,text="Reference:").grid(row=8,column=0)
            Label(self.BWindow,text=str(self.settings.Channel2ReferenceRes)+" Ω "+ "at 298,15 K").grid(row=8,column=1)
            Label(self.BWindow,text="Coefficient:").grid(row=9,column=0)
            Label(self.BWindow,text=str(self.settings.Channel2BCoefficient)+"K").grid(row=9,column=1)
            Label(self.BWindow,text="Probe resistance:").grid(row=10,column=0)
            Label(self.BWindow,text=str(self.settings.Channel2ProbeRes)+" Ω").grid(row=10,column=1)
            Label(self.BWindow,text="Chart Y axis").grid(row=12,column=0)
            Label(self.BWindow,text="Minimum").grid(row=13,column=0)
            Label(self.BWindow,text="Maximum").grid(row=16,column=0)
            Label(self.BWindow,text="Level-crossing detector").grid(row=18,column=0)
            Label(self.BWindow,text="Level").grid(row=20,column=0)
            Label(self.BWindow,text="Hysteresis").grid(row=22,column=0)
            Label(self.BWindow,text="Object length [m]").grid(row=24,column=0)

            self.HideSubplotB.grid(row=0,column=0)
            self.ColorB.grid(row=0,column=1)
            self.SetChannelBType.grid(row=2,column=0,columnspan=2)
            self.ChannelBLinTherm.grid(row=4,column=1)
            self.EntryChannelBName.grid(row=5,column=1)
            self.EntryChannelBQuantity.grid(row=6,column=1)
            self.EntryChannelBUnit.grid(row=7,column=1)
            self.EditBSensorButton.grid(row=11,column=0,columnspan=2)
            self.EntryBylimitBot.grid(row=14,column=0)
            self.ChannelBButoscale.grid(row=15,column=1)
            self.EntryBylimitTop.grid(row=17,column=0)
            self.ChannelBLevelcrossing.grid(row=19,column=0)
            self.EntryBLevelcrossingLevel.grid(row=21,column=0)
            self.EntryBLevelcrossingHyst.grid(row=23,column=0)
            self.EntryBLevelcrossingObjLen.grid(row=25,column=0)


            if not(self.pause):
                self.ChannelBLinTherm['state'] = DISABLED
                self.EntryChannelBName['state'] = DISABLED
                self.EntryChannelBQuantity['state'] = DISABLED
                self.EntryChannelBUnit['state'] = DISABLED
                self.EditBSensorButton['state'] = DISABLED

    def openCWindow(self):
        if self.CWindow == None or not(tkinter.Toplevel.winfo_exists(self.CWindow)):
            self.CWindow = Toplevel(self.root)
            self.CWindow.title("C settings")
            self.HideSubplotC = Button(self.CWindow,text="HideSubplotC",command=lambda: self.HideSubplot("C"))
            self.ColorC = Button(self.CWindow,text="color",bg=self.settings.line3Color,command= lambda: self.ChangeLineColor("C"))
            self.SetChannelCType = OptionMenu(self.CWindow,self.settings.Channel3Typevar,"voltage","resistor","inamp","photo")
            self.ChannelCLinTherm = OptionMenu(self.CWindow,self.Channel3LinTherm,"Linear","Thermistor")
            self.EntryChannelCName = Entry(self.CWindow,textvariable=self.Channel3Name)
            self.EntryChannelCQuantity = Entry(self.CWindow,textvariable=self.Channel3Quantityvar)
            self.EntryChannelCUnit = Entry(self.CWindow,textvariable=self.Channel3Unit)
            self.EditCSensorButton = Button(self.CWindow,text="Edit sensor",pady=10)       
            self.EntryCylimitBot = Entry(self.CWindow,textvariable=self.ylimitCbotvar)
            self.EntryCylimitTop = Entry(self.CWindow,textvariable=self.ylimitCtopvar)
            self.ChannelCCutoscale = Checkbutton(self.CWindow,text="Autoscale", variable=self.automatic_scaleC)
            self.ChannelCLevelcrossing = Checkbutton(self.CWindow,text="Active", variable=self.LevelcrossingonC)
            self.EntryCLevelcrossingLevel = Entry(self.CWindow,textvariable=self.LevelCrossingLevelCvar)
            self.EntryCLevelcrossingHyst = Entry(self.CWindow,textvariable=self.LevelCrossingHystCvar)
            self.EntryCLevelcrossingObjLen = Entry(self.CWindow,textvariable=self.LevelCrossingObjLenCvar)

            Label(self.CWindow,text="Sensor interfacing",pady=10).grid(row=1,column=0,columnspan=2)
            Label(self.CWindow,text="Sensor").grid(row=3,column=0)
            Label(self.CWindow,text="Type").grid(row=4,column=0)
            Label(self.CWindow,text="Name").grid(row=5,column=0)
            Label(self.CWindow,text="Quantity").grid(row=6,column=0)
            Label(self.CWindow,text="Unit").grid(row=7,column=0)
            Label(self.CWindow,text="Reference:").grid(row=8,column=0)
            Label(self.CWindow,text=str(self.settings.Channel3ReferenceRes)+" Ω "+ "at 298,15 K").grid(row=8,column=1)
            Label(self.CWindow,text="Coefficient:").grid(row=9,column=0)
            Label(self.CWindow,text=str(self.settings.Channel3BCoefficient)+"K").grid(row=9,column=1)
            Label(self.CWindow,text="Probe resistance:").grid(row=10,column=0)
            Label(self.CWindow,text=str(self.settings.Channel3ProbeRes)+" Ω").grid(row=10,column=1)
            Label(self.CWindow,text="Chart Y axis").grid(row=12,column=0)
            Label(self.CWindow,text="Minimum").grid(row=13,column=0)
            Label(self.CWindow,text="Maximum").grid(row=16,column=0)
            Label(self.CWindow,text="Level-crossing detector").grid(row=18,column=0)
            Label(self.CWindow,text="Level").grid(row=20,column=0)
            Label(self.CWindow,text="Hysteresis").grid(row=22,column=0)
            Label(self.CWindow,text="Object length [m]").grid(row=24,column=0)

            self.HideSubplotC.grid(row=0,column=0)
            self.ColorC.grid(row=0,column=1)
            self.SetChannelCType.grid(row=2,column=0,columnspan=2)
            self.ChannelCLinTherm.grid(row=4,column=1)
            self.EntryChannelCName.grid(row=5,column=1)
            self.EntryChannelCQuantity.grid(row=6,column=1)
            self.EntryChannelCUnit.grid(row=7,column=1)
            self.EditCSensorButton.grid(row=11,column=0,columnspan=2)
            self.EntryCylimitBot.grid(row=14,column=0)
            self.ChannelCCutoscale.grid(row=15,column=1)
            self.EntryCylimitTop.grid(row=17,column=0)
            self.ChannelCLevelcrossing.grid(row=19,column=0)
            self.EntryCLevelcrossingLevel.grid(row=21,column=0)
            self.EntryCLevelcrossingHyst.grid(row=23,column=0)
            self.EntryCLevelcrossingObjLen.grid(row=25,column=0)


            if not(self.pause):
                self.ChannelCLinTherm['state'] = DISABLED
                self.EntryChannelCName['state'] = DISABLED
                self.EntryChannelCQuantity['state'] = DISABLED
                self.EntryChannelCUnit['state'] = DISABLED
                self.EditCSensorButton['state'] = DISABLED

    def popupmenu(self,buttpress):
        self.Chartmenu.tk_popup(buttpress.x_root,buttpress.y_root)

    def LCPopupMenu(self,buttpress,channel):
        if channel == "A":
            self.LcChart.tk_popup(buttpress.x_root,buttpress.y_root)
        if channel == "B":
            self.LcChart1.tk_popup(buttpress.x_root,buttpress.y_root)
        if channel == "C":
            self.LcChart2.tk_popup(buttpress.x_root,buttpress.y_root)

    def SaveDataAsImage(self):
        try:
            filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save Image",filetypes=(("Png",".png"),("Svg",".svg"),("All Files","*.*")))
            plt.savefig(filename)
        except:
            pass

    def Copydata(self):
        df = pd.DataFrame(self.plotdata,columns=['t','A','B','C'])
        df = df[self.settings.ShownColumns]
        df.to_clipboard(index=False,header=True)

    def ManageChannelTypes(*args):
        WidgetName = args[1]
        if WidgetName == "Atype":
            value = args[0].settings.Channel1Typevar.get()
            if value == "voltage":
                args[0].settings.Channel1Type = edaqcomm.ChannelType.voltage
            if value == "resistor":
                args[0].settings.Channel1Type = edaqcomm.ChannelType.resistor
            if value == "inamp":
                args[0].settings.Channel1Type = edaqcomm.ChannelType.inamp
            if value == "photo":
                args[0].settings.Channel1Type = edaqcomm.ChannelType.photo

        if WidgetName == "Btype":
            value = args[0].settings.Channel2Typevar.get()
            if value == "voltage":
                args[0].settings.Channel2Type = edaqcomm.ChannelType.voltage
            if value == "resistor":
                args[0].settings.Channel2Type = edaqcomm.ChannelType.resistor
            if value == "inamp":
                args[0].settings.Channel2Type = edaqcomm.ChannelType.inamp
            if value == "photo":
                args[0].settings.Channel2Type = edaqcomm.ChannelType.photo

        if WidgetName == "Ctype":
            value = args[0].settings.Channel3Typevar.get()
            if value == "voltage":
                args[0].settings.Channel3Type = edaqcomm.ChannelType.voltage
            if value == "resistor":
                args[0].settings.Channel3Type = edaqcomm.ChannelType.resistor
            if value == "inamp":
                args[0].settings.Channel3Type = edaqcomm.ChannelType.inamp
            if value == "photo":
                args[0].settings.Channel3Type = edaqcomm.ChannelType.photo

        args[0].comm.setInputs(args[0].settings.Channel1Type,args[0].settings.Channel2Type,args[0].settings.Channel3Type)

    def LineIntersectsLevel(self,x1,y1,x2,y2,level):
        return round((((x2-x1)*(level-y1))/(y2-y1))+x1,3)
          
    def InsertToChart(self,channel,prop,value):
        if prop != 0:
            self.LatestHystData[channel][prop] = value
        else:
            self.LatestHystData[channel][0] = value
            self.LatestHystData[channel][1] = ''
            self.LatestHystData[channel][2] = ''
        if channel == "A":
            if prop == 0:
                if len(self.tree.get_children()) % 2  == 0:
                    self.tree.insert('',END, values=self.LatestHystData[channel],tags=("evenrow",))
                else:
                    self.tree.insert('',END, values=self.LatestHystData[channel],tags=("oddrow",))
            if prop != 0:
                last_id = self.tree.get_children()[-1]
                self.tree.item(last_id,values=self.LatestHystData[channel]) 

        if channel == "B":
            if prop == 0:
                if len(self.tree1.get_children()) % 2  == 0:
                    self.tree1.insert('',END, values=self.LatestHystData[channel],tags=("evenrow",))
                else:
                    self.tree1.insert('',END, values=self.LatestHystData[channel],tags=("oddrow",))
            if prop != 0:
                last_id = self.tree1.get_children()[-1]
                self.tree1.item(last_id,values=self.LatestHystData[channel]) 
        
        if channel == "C":
            if prop == 0:
                if len(self.tree2.get_children()) % 2  == 0:
                    self.tree2.insert('',END, values=self.LatestHystData[channel],tags=("evenrow",))
                else:
                    self.tree2.insert('',END, values=self.LatestHystData[channel],tags=("oddrow",))
            if prop != 0:
                last_id = self.tree2.get_children()[-1]
                self.tree2.item(last_id,values=self.LatestHystData[channel]) 

    def LevelCrossingDetection(self,channel,y,hyst,level,objlen,goingup,points):        
        x = self.plotdata[:,0]
        #check if we're going up and if we passed the bottom hyst line
        if y[-1]<level:
            points[0] = [x[-1],y[-1]]
            if goingup.get()==0:

                intersect = self.LineIntersectsLevel(points[0][0],points[0][1],points[1][0],points[1][1],level)
                Speed = objlen/(intersect-self.LatestHystData[channel][0])
                self.InsertToChart(channel,2,Speed)                
                #print(channel+" lement: "+ str(self.LineIntersectsLevel(points[1][0],points[1][1],points[0][0],points[0][1],level)))

            goingup.set(1)

        #check if we got through the top hyst  
        if y[-1]>(level+hyst):
            points[1] = [x[-1],y[-1]]
            if goingup.get():
                #Time [s], Period[s]
                #we crossed the top hyst add time[s] and period[s]
                intersect = self.LineIntersectsLevel(points[1][0],points[1][1],points[0][0],points[0][1],level)
                if self.LatestHystData[channel][0] != '':
                    new_period = intersect-self.LatestHystData[channel][0]
                    #insert Period[s]
                    self.InsertToChart(channel,1,new_period)    
                    self.HystData[channel].append(list(self.LatestHystData[channel]))
                #insert the Time [s],
                self.InsertToChart(channel,0,intersect)

                #print(channel+" fölment: "+ str(self.LineIntersectsLevel(points[0][0],points[0][1],points[1][0],points[1][1],level)))
            goingup.set(0)
          
            
    #Beállítja a levelcrossing változók értékét a beírtakra
    def SetLevelCrossingVariables(self,level,levelset,hyst,hystset,objlen,objlenset):
        try:
            level.set(float(levelset.get()))
            hyst.set(float(hystset.get()))
            objlen.set(float(objlenset.get()))            
        except:
            pass

    def load_measurements(self):
        filedata = self.settings.LoadSettings()
        self.clear_data()
        self.HideSubplot(None)
        self.settings.LoadSetup(filedata)


    def setuptkinter(self):
        #setting up visual and interactive elements
        self.root.geometry("700x300")
        
        self.root["bg"] = "blue"
        self.root.title("Edaq függvény demo")
        label = Label(self.root,text="Mérés:")
        label.grid(row=0)
        self.startbutton = Button(self.root,text="start",command=self.start_charts)
        self.stopbutton = Button(self.root,text="stop",command=self.stop_charts)
        self.ChartVisibleButton = Button(self.root,text="make disappear",command=self.hide_chart)
        self.ClearDataButton = Button(self.root,text="Reset Charts",command=self.clear_data)
        self.SaveDataTxtButton = Button(self.root,text="Save Data to txt",command=lambda: self.data.save_data(self.settings.ShownColumns,"txt"))
        self.SaveDataExcelButton = Button(self.root,text="Save Data to excel",command=lambda: self.data.save_data(self.settings.ShownColumns,"xlsx"))
        self.HideSubplotA = Button(self.root,text="HideSubplotA",command=lambda: self.HideSubplot("A"))
        self.HideSubplotB = Button(self.root,text="HideSubplotB",command=lambda: self.HideSubplot("B"))
        self.HideSubplotC = Button(self.root,text="HideSubplotC",command=lambda: self.HideSubplot("C"))
        self.SetChannelAType = OptionMenu(self.root,self.settings.Channel1Typevar,"voltage","resistor","inamp","photo")
        self.SetChannelBType = OptionMenu(self.root,self.settings.Channel2Typevar,"voltage","resistor","inamp","photo")
        self.SetChannelCType = OptionMenu(self.root,self.settings.Channel3Typevar,"voltage","resistor","inamp","photo")
        self.ChannelAAutoscale = Checkbutton(self.root,text="Channel A autoscale", variable=self.automatic_scaleA)
        self.ChannelBAutoscale = Checkbutton(self.root,text="Channel B autoscale", variable=self.automatic_scaleB)
        self.ChannelCAutoscale = Checkbutton(self.root,text="Channel C autoscale", variable=self.automatic_scaleC)
        self.ASensorSettings = Button(self.root,text="Set A channel variables",command=self.openAWindow)
        self.BSensorSettings = Button(self.root,text="Set B channel variables",command=self.openBWindow)
        self.CSensorSettings = Button(self.root,text="Set C channel variables",command=self.openCWindow)

        #Setting up right click menu bar
        self.Chartmenu = Menu(self.root,tearoff=False)
        self.Chartmenu.add_command(label="Save as image",command=self.SaveDataAsImage)
        self.Chartmenu.add_command(label="Save to excel",command=lambda: self.data.save_data(self.settings.ShownColumns,"xlsx"))
        self.Chartmenu.add_command(label="Copy to clipboard",command=self.Copydata)
        self.Chartmenu.add_command(label="Reset", command=self.clear_data)

        #Setting up Lc menu bar
        self.LcChart = Menu(self.root,tearoff=False)
        self.LcChart.add_command(label="Copy data to clipboard",command=lambda: self.CopyLcData("A"))
        self.LcChart.add_command(label="clear",command=lambda: self.ClearLcData("A"))

        self.LcChart1 = Menu(self.root,tearoff=False)
        self.LcChart1.add_command(label="Copy data to clipboard",command=lambda: self.CopyLcData("B"))
        self.LcChart1.add_command(label="clear",command=lambda: self.ClearLcData("B"))

        self.LcChart2 = Menu(self.root,tearoff=False)
        self.LcChart2.add_command(label="Copy data to clipboard",command=lambda: self.CopyLcData("C"))
        self.LcChart2.add_command(label="clear",command=lambda: self.ClearLcData("C"))


        #Setting up the menu bar
        self.menubar = Menu(self.root,background="#565656")
        self.ConnexionMenu = Menu(self.root,tearoff=0)
        self.filemenu = Menu(self.menubar,tearoff=0)
        self.SaveSensorMenu = Menu(self.filemenu,tearoff=0)
        self.LoadSensorMenu = Menu(self.filemenu,tearoff=0)

        self.ConnexionMenu.add_command(label="Rescan devices    Ctrl+R",command=self.tryConnection)
        self.menubar.add_cascade(label="Connexion",menu=self.ConnexionMenu)

        self.SaveSensorMenu.add_command(label="From Channel A   Ctrl+alt+A",command=lambda: self.settings.SaveA(True))
        self.SaveSensorMenu.add_command(label="From Channel B   Ctrl+alt+B",command=lambda: self.settings.SaveB(True))
        self.SaveSensorMenu.add_command(label="From Channel C   Ctrl+alt+C",command=lambda: self.settings.SaveC(True))
        self.filemenu.add_cascade(label="Save Sensor...",menu=self.SaveSensorMenu)

        self.LoadSensorMenu.add_command(label="To Channel A   Alt+A",command=self.settings.LoadSettingsA)
        self.LoadSensorMenu.add_command(label="To Channel B   Alt+B",command=self.settings.LoadSettingsB)
        self.LoadSensorMenu.add_command(label="To Channel C   Alt+C",command=self.settings.LoadSettingsC)

        self.filemenu.add_cascade(label="Load sensor from file...",menu=self.LoadSensorMenu)
        self.filemenu.add_command(label="Save Measurment setup...   Ctrl+S",command=self.settings.SaveSettings)
        self.filemenu.add_command(label="Load Measurment setup...   Ctrl+L",command=self.load_measurements)
        self.filemenu.add_command(label="Save Measurment data to txt...    Ctrl+D",command=lambda: self.data.save_data(self.settings.ShownColumns,"txt"))
        self.filemenu.add_command(label="Save Measurment data to xlsx...    Ctrl+E",command=lambda: self.data.save_data(self.settings.ShownColumns,"xlsx"))
        self.menubar.add_cascade(label="File",menu=self.filemenu)

        self.menubar.add_command(label="Start/Stop",command=self.start_or_stop_charts)
        self.menubar.add_command(label="Reset Charts",command=self.clear_data)
        self.menubar.add_separator()
        self.menubar.add_checkbutton(label="A",onvalue=1,offvalue=0,variable=self.settings.AisShown,command=lambda: self.ManageShownChannels("A"))
        self.menubar.add_checkbutton(label="B",onvalue=1,offvalue=0,variable=self.settings.BisShown,command=lambda: self.ManageShownChannels("B"))
        self.menubar.add_checkbutton(label="C",onvalue=1,offvalue=0,variable=self.settings.CisShown,command=lambda: self.ManageShownChannels("C"))
        self.root.config(menu=self.menubar)

        self.EntrySamplingFreq = Entry(self.root,textvariable=self.samplingfreqval)
        self.AveragingMenu = OptionMenu(self.root,self.averagingvar,"No averaging","4 Averages","8 Averages","16 Averages")
        self.EntryTitle = Entry(self.root,textvariable=self.title)
        self.EntryTimeFramesec = Entry(self.root,textvariable=self.timeframesecvar)
        self.EntryTimeFramePoints = Entry(self.root,textvariable=self.timeframepointsvar)
        self.EntryRefreshRate = Entry(self.root,textvariable=self.refreshrate)

        #putting the visual elements in a grid
        self.startbutton.grid(row=1,column=1)
        self.stopbutton.grid(row=2,column=1)
        self.ChartVisibleButton.grid(row=3,column=1)
        self.ClearDataButton.grid(row=4,column=1)
        self.SaveDataTxtButton.grid(row=5,column=1)
        self.SaveDataExcelButton.grid(row=6,column=1)
        self.HideSubplotA.grid(row=7,column=1)
        self.HideSubplotB.grid(row=8,column=1)
        self.HideSubplotC.grid(row=9,column=1)

        self.SetChannelAType.grid(row=1,column=2)
        self.SetChannelBType.grid(row=2,column=2)
        self.SetChannelCType.grid(row=3,column=2)
        self.ChannelAAutoscale.grid(row=4,column=2)
        self.ChannelBAutoscale.grid(row=5,column=2)
        self.ChannelCAutoscale.grid(row=6,column=2)
        self.ASensorSettings.grid(row=7,column=2)
        self.BSensorSettings.grid(row=8,column=2)
        self.CSensorSettings.grid(row=9,column=2)

        #Configuring keyboard shortcuts
        self.canvas.get_tk_widget().bind("<Button-3>",self.popupmenu)

        self.root.bind("<Control-s>",lambda event: self.settings.SaveSettings())
        self.root.bind("<Control-r>",lambda event: self.tryConnection())
        
        self.root.bind("<Control-Alt-a>",lambda event: self.settings.SaveA(True))
        self.root.bind("<Control-Alt-b>",lambda event: self.settings.SaveB(True))
        self.root.bind("<Control-Alt-c>",lambda event: self.settings.SaveC(True))
        
        self.root.bind("<Alt-a>",lambda event: self.settings.LoadSettingsA())
        self.root.bind("<Alt-b>",lambda event: self.settings.LoadSettingsB())
        self.root.bind("<Alt-c>",lambda event: self.settings.LoadSettingsC())

        self.root.bind("<Control-l>",lambda event: self.settings.LoadSettings())
        self.root.bind("<Control-d>",lambda event: self.data.save_data(self.settings.ShownColumns,"txt"))
        self.root.bind("<Control-e>",lambda event: self.data.save_data(self.settings.ShownColumns,"xlsx"))

        Label(self.root,text="Sampling").grid(row=1,column=3)
        Label(self.root,text="Sampling frequency [Hz]").grid(row=2,column=3)
        self.EntrySamplingFreq.grid(row=3,column=3)
        self.AveragingMenu.grid(row=4,column=3)
        Label(self.root,text="Time scale").grid(row=5,column=3)
        Label(self.root,text="Title").grid(row=6,column=3)
        self.EntryTitle.grid(row=7,column=3)
        Label(self.root,text="Time frame [s]").grid(row=8,column=3)
        self.EntryTimeFramesec.grid(row=9,column=3)
        Label(self.root,text="Time frame (in points)").grid(row=10,column=3)
        self.EntryTimeFramePoints.grid(row=11,column=3)
        Label(self.root,text="Refresh rate [Hz]").grid(row=12,column=3)
        self.EntryRefreshRate.grid(row=13,column=3)


    def tryConnection(self):
        if not self.connected:
            for i in range(5):
                newport = "/dev/ttyUSB" + str(i)
                try:
                    self.setConnection(newport)
                    if self.connected == True:
                        print("Edaq found")
                        #Enable start button and freq settings
                        self.startbutton["state"] = NORMAL
                        self.menubar.entryconfig(3,state=NORMAL)
                        self.EntrySamplingFreq["state"] = NORMAL
                        return 0
                except:
                    pass
            print("Couldn't find edaq")
            messagebox.showerror("Error","Couldn't find edaq device")
            #Disable start button and freq settings
            self.startbutton["state"] = DISABLED
            self.menubar.entryconfig(3,state=DISABLED)
            self.EntrySamplingFreq["state"] = DISABLED
        else:
            print("Edaq already connected")


    def setConnection(self,port):
        self.comm = edaqcomm.Edaq530Comm(port)
        self.comm.connect()
        self.comm.flushBuffers()
        self.comm.setInputs(edaqcomm.ChannelType.voltage,
            edaqcomm.ChannelType.voltage, edaqcomm.ChannelType.voltage)
        self.connected = True
        #self.comm.setSamplingFreq(1000)

    
    def UpdateData(self):
            while True:
                a = time.time()
                time.process_time()
                time.perf_counter()
                if not self.pause:
                    measured = self.comm.measure() #self.comm.measureWithoutChecking()
                    y1 = edaqcomm.getMeasuredQuantity(measured[0],self.settings.Channel1Quantity)
                    y2 = edaqcomm.getMeasuredQuantity(measured[1],self.settings.Channel2Quantity)
                    y3 = edaqcomm.getMeasuredQuantity(measured[2],self.settings.Channel3Quantity)
                    x = time.time()-self.startedat-self.alltimepaused
                    data = np.array([[x,y1,y2,y3]])
                    self.data.add_data(x,y1,y2,y3)
                    
                    self.plotdata = np.concatenate((self.plotdata[1:],data),axis=0)
                    
                #print(1/(time.time()-a),"   ",time.process_time(),"    ",time.perf_counter())

    def UpdatePlot(self,i):
        if not self.pause:
            if "A" in self.settings.ShownColumns:
                # here we manage the level crossing lines
                if self.LevelcrossingonA.get():
                    # Generate the line "data"
                    levelcrossingmin = np.zeros(self.settings.timeframepoints) + self.settings.LevelCrossingLevelA - self.settings.LevelCrossingHystA
                    levelcrossingmax = np.zeros(self.settings.timeframepoints) + self.settings.LevelCrossingLevelA + self.settings.LevelCrossingHystA
                    #setup levelcrossing lines
                    self.linelevelcrossingmin.set_data(self.plotdata[:,0],levelcrossingmin)
                    self.linelevelcrossingmax.set_data(self.plotdata[:,0],levelcrossingmax)
                
                if self.LevelcrossingonA.get():
                    self.LevelCrossingDetection("A",self.plotdata[:,1],self.settings.LevelCrossingHystA,self.settings.LevelCrossingLevelA,self.settings.LevelCrossingObjLenA,self.AGoingUp,self.LevelCrossingPointsA)

                #updating the graph ilnes with the new data   
                self.line.set_data(self.plotdata[:,0],self.plotdata[:,1])                
                self.Alabel['text'] = "%s = %s %s" % (self.Channel1Quantityvar.get(),str(round(self.plotdata[-1][1],2)),self.Channel1Unit.get())
                #Displaying data based on autoscale
                if self.automatic_scaleA.get():
                    #here I display data where the top and bottom of the graph are based on out measurements
                    self.ax.axis([self.plotdata[0,0],self.plotdata[-1,0],min(self.plotdata[:,1]),max(self.plotdata[:,1])])
                else:
                    #Here the top and bottom of the graph are based on the ylimit variables
                    self.ax.axis([self.plotdata[0,0],self.plotdata[-1,0],self.settings.ylimitAbot,self.settings.ylimitAtop])

            if "B" in self.settings.ShownColumns:
                # here we manage the level crossing lines
                if self.LevelcrossingonB.get():
                    levelcrossingmin = np.zeros(self.settings.timeframepoints) + self.settings.LevelCrossingLevelB - self.settings.LevelCrossingHystB
                    levelcrossingmax = np.zeros(self.settings.timeframepoints) + self.settings.LevelCrossingLevelB + self.settings.LevelCrossingHystB
                    self.line2levelcrossingmin.set_data(self.plotdata[:,0],levelcrossingmin)
                    self.line2levelcrossingmax.set_data(self.plotdata[:,0],levelcrossingmax)

                if self.LevelcrossingonB.get():
                    self.LevelCrossingDetection("B",self.plotdata[:,2],self.settings.LevelCrossingHystB,self.settings.LevelCrossingLevelB,self.settings.LevelCrossingObjLenB,self.BGoingUp,self.LevelCrossingPointsB)

                #updating the graph ilnes with the new data   
                self.line2.set_data(self.plotdata[:,0], self.plotdata[:,2])

                self.Blabel['text'] = "%s = %s %s" % (self.Channel2Quantityvar.get(),str(round(self.plotdata[-1][2],2)),self.Channel2Unit.get())

                if self.automatic_scaleB.get():
                    self.ax2.axis([self.plotdata[0,0],self.plotdata[-1,0],min(self.plotdata[:,2]),max(self.plotdata[:,2])])
                else:
                    self.ax2.axis([self.plotdata[0,0],self.plotdata[-1,0],self.settings.ylimitBbot,self.settings.ylimitBtop])


            if "C" in self.settings.ShownColumns:
                # here we manage the level crossing lines        
                if self.LevelcrossingonC.get():
                    levelcrossingmin = np.zeros(self.settings.timeframepoints) + self.settings.LevelCrossingLevelC - self.settings.LevelCrossingHystC
                    levelcrossingmax = np.zeros(self.settings.timeframepoints) + self.settings.LevelCrossingLevelC + self.settings.LevelCrossingHystC
                    self.line3levelcrossingmin.set_data(self.plotdata[:,0],levelcrossingmin)
                    self.line3levelcrossingmax.set_data(self.plotdata[:,0],levelcrossingmax)
        
                if self.LevelcrossingonC.get():
                    self.LevelCrossingDetection("C",self.plotdata[:,3],self.settings.LevelCrossingHystC,self.settings.LevelCrossingLevelC,self.settings.LevelCrossingObjLenC,self.CGoingUp,self.LevelCrossingPointsC)

                #updating the graph ilnes with the new data   
                self.line3.set_data(self.plotdata[:,0], self.plotdata[:,3])
            
                self.Clabel['text'] = "%s = %s %s" % (self.Channel3Quantityvar.get(),str(round(self.plotdata[-1][3],2)),self.Channel3Unit.get())

                if self.automatic_scaleC.get():
                    self.ax3.axis([self.plotdata[0,0],self.plotdata[-1,0],min(self.plotdata[:,3]),max(self.plotdata[:,3])])
                else:
                    self.ax3.axis([self.plotdata[0,0],self.plotdata[-1,0],self.settings.ylimitCbot,self.settings.ylimitCtop])

s = some()
