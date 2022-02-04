from os import name, path
from tkinter import IntVar, StringVar, DoubleVar, Tk
from xml.dom import minidom
import xml.etree.ElementTree as ET
from tkinter import filedialog
import edaqcomm

class Settings():
    def __init__(self):
        if __name__ == "__main__":
            self.root = Tk() # Take out later **************

        self.axNumOfPins = 5
        self.ax2NumOfPins = 5
        self.ax3NumOfPins = 5
        

        self.port = "/dev/ttyUSB0"


        #axis labels        
        self.ax1Ylabel = "U [V]"
        self.ax2Ylabel = "U [V]"
        self.ax3Ylabel = "U [V]"

        #setting up the line colors
        self.line1Color = "#ffa600"
        self.line2Color = "#00b503"
        self.line3Color = "#045ad1"

        #Setting up some variables
        
        self.samplingfreqval = StringVar(name="SamplingFreq",value=10)
        self.samplingfreq = float(self.samplingfreqval.get())

        self.averagingvar = StringVar(name="Averagingvar",value="No averaging")
        self.averaging = -1

        self.title = StringVar(name="XAxesTitle",value="t [s]")
        
        self.timeframesecvar = StringVar(value=2,name="Seconds")
        self.timeframesec = float(self.timeframesecvar.get())

        self.timeframepointsvar = StringVar(value=str(round(self.samplingfreq)*round(self.timeframesec)),name="Points")
        self.timeframepoints = int(self.timeframepointsvar.get())

        self.refreshrate = DoubleVar(value=50,name="Refreshrate")

        self.timeincrement = 1/self.samplingfreq
        self.pause = True
        self.ylimitAtopvar = DoubleVar(value=2,name="Atop")
        self.ylimitAbotvar = DoubleVar(value=0,name="Abot")
        self.ylimitBtopvar = DoubleVar(value=6,name="Btop")
        self.ylimitBbotvar = DoubleVar(value=-1,name="Bbot")
        self.ylimitCtopvar = DoubleVar(value=6,name="Ctop")
        self.ylimitCbotvar = DoubleVar(value=-1,name="Cbot")

        self.ylimitAbot = self.ylimitAbotvar.get()
        self.ylimitAtop = self.ylimitAtopvar.get()
        self.ylimitBbot = self.ylimitBbotvar.get()
        self.ylimitBtop = self.ylimitBtopvar.get()
        self.ylimitCbot = self.ylimitCbotvar.get()
        self.ylimitCtop = self.ylimitCtopvar.get()

        self.visible = True

        #toggle the columns that are shown
        self.ShownColumns = ["t","A","C"]

        #Popup windows for demo settings
        self.AWindow = None
        self.BWindow = None
        self.CWindow = None

        #setting channel type
        self.Channel1Type = edaqcomm.ChannelType.voltage
        self.Channel2Type = edaqcomm.ChannelType.resistor
        self.Channel3Type = edaqcomm.ChannelType.voltage

        self.Channel1Typevar = StringVar(name="Atype",value="voltage")
        self.Channel2Typevar = StringVar(name="Btype",value="resistor")
        self.Channel3Typevar = StringVar(name="Ctype",value="voltage")
       
        #sensor settings quantity
        self.Channel1Quantity = edaqcomm.QuantityType.voltage
        self.Channel2Quantity = edaqcomm.QuantityType.resistance
        self.Channel3Quantity = edaqcomm.QuantityType.temp_celsius

        self.Channel1Quantityvar = StringVar(name="Aquantity",value="")
        self.Channel2Quantityvar = StringVar(name="Bquantity",value="")
        self.Channel3Quantityvar = StringVar(name="Cquantity",value="T")

        self.Channel1LinTherm = StringVar(name="Ch1lintherm",value="Linear")
        self.Channel2LinTherm = StringVar(name="Ch2lintherm",value="Linear")
        self.Channel3LinTherm = StringVar(name="Ch3lintherm",value="Thermistor")

        self.Channel1Name = StringVar(name="Aname",value="Jani")
        self.Channel2Name = StringVar(name="Bname",value="Janetta")
        self.Channel3Name = StringVar(name="Cname",value="Jeromos")

        self.Channel1Unit = StringVar(name="AUnit",value="G")
        self.Channel2Unit = StringVar(name="BUnit",value="V")
        self.Channel3Unit = StringVar(name="CUnit",value="°C")

        self.Channel1Intercept = 2
        self.Channel2Intercept = 0
        self.Channel3Intercept = 0

        self.Channel1Slope = 1.2
        self.Channel2Slope = 1
        self.Channel3Slope = 1

        self.Channel1ReferenceRes = 10000
        self.Channel2ReferenceRes = 10000
        self.Channel3ReferenceRes = 105

        self.Channel1BCoefficient = 3977
        self.Channel2BCoefficient = 3977
        self.Channel3BCoefficient = 3977

        self.Channel1ProbeRes = 10000
        self.Channel2ProbeRes = 10000
        self.Channel3ProbeRes = 10000

        #setting automatic y axis scaling
        self.automatic_scaleA = IntVar(name="AutomaticScaleA",value=0)
        self.automatic_scaleB = IntVar(name="AutomaticScaleB",value=1)
        self.automatic_scaleC = IntVar(name="AutomaticScaleC",value=0)

        #Level crossing detection variables
        self.LevelcrossingonA = IntVar(name="LevelCrossingOnA",value=1)
        self.LevelcrossingonB = IntVar(name="LevelCrossingOnB",value=0)
        self.LevelcrossingonC = IntVar(name="LevelCrossingOnC",value=1)

        self.LevelCrossingLevelAvar = DoubleVar(value=3.0,name="Alevel") 
        self.LevelCrossingLevelBvar = DoubleVar(value=2.0,name="Blevel")
        self.LevelCrossingLevelCvar = DoubleVar(value=1.0,name="Clevel")

        self.LevelCrossingHystAvar = DoubleVar(value=0.25,name="AHyst")
        self.LevelCrossingHystBvar = DoubleVar(value=0.0,name="BHyst")
        self.LevelCrossingHystCvar = DoubleVar(value=0.5,name="CHyst")

        self.LevelCrossingObjLenAvar = DoubleVar(value=0.3,name="AObjLen")
        self.LevelCrossingObjLenBvar = DoubleVar(value=0.1,name="BObjLen")
        self.LevelCrossingObjLenCvar = DoubleVar(value=0.2,name="CObjLen")


        self.LevelCrossingLevelA = self.LevelCrossingLevelAvar.get()
        self.LevelCrossingLevelB = self.LevelCrossingLevelBvar.get()
        self.LevelCrossingLevelC = self.LevelCrossingLevelCvar.get()

        self.LevelCrossingHystA = self.LevelCrossingHystAvar.get()
        self.LevelCrossingHystB = self.LevelCrossingHystBvar.get()
        self.LevelCrossingHystC = self.LevelCrossingHystCvar.get()

        self.LevelCrossingObjLenA = self.LevelCrossingObjLenAvar.get()
        self.LevelCrossingObjLenB = self.LevelCrossingObjLenBvar.get()
        self.LevelCrossingObjLenC = self.LevelCrossingObjLenCvar.get()


    def AddElement(self,doc,parent,name,text):
            child = doc.createElement(name)            
            parent.appendChild(child)
            if text != "":
                textnode = doc.createTextNode(str(text))
                child.appendChild(textnode)
            return child

    def AddElementWAttr(self,doc,parent,name,attributes,text):
        child = doc.createElement(name)
        for i in attributes:
            child.setAttribute(i,attributes[i])
        parent.appendChild(child)
        if text != "":
            textnode = doc.createTextNode(str(text))
            child.appendChild(textnode)
        return child
    
    def SetAveragingvar(self):
        if self.averaging == -1:
            self.averagingvar.set("No averaging")
        elif self.averaging == 4:
            self.averagingvar.set("4 averages")
        elif self.averaging == 8:
            self.averagingvar.set("8 averages")
        elif self.averaging == 16:
            self.averagingvar.set("16 averages")

    def SetText(self,doc,parent,text):
        textnode = doc.createTextNode(text)
        parent.appendChild(textnode)

    def Setquantity(self,channel):
        if channel == "A":
            if self.Channel1LinTherm.get() == "Thermistor":
                if self.Channel1Unit.get() == "°C":
                    self.Channel1Quantity = edaqcomm.QuantityType.temp_celsius
                elif self.Channel1Unit.get() == "K":
                    self.Channel1Quantity = edaqcomm.QuantityType.temp_kelvin
            elif self.Channel1LinTherm.get() == "Linear":
                if self.Channel1Typevar.get() == "voltage":
                    self.Channel1Quantity = edaqcomm.QuantityType.voltage
                if self.Channel1Typevar.get() == "resistor":
                    self.Channel1Quantity = edaqcomm.QuantityType.resistance

        elif channel == "B":
            if self.Channel2LinTherm.get() == "Thermistor":
                if self.Channel2Unit == "°C":
                    self.Channel2Quantity = edaqcomm.QuantityType.temp_celsius
                elif self.Channel2Unit == "K":
                    self.Channel2Quantity = edaqcomm.QuantityType.temp_kelvin
            elif self.Channel2LinTherm.get() == "Linear":
                if self.Channel2Typevar.get() == "voltage":
                    self.Channel2Quantity = edaqcomm.QuantityType.voltage
                if self.Channel2Typevar.get() == "resistor":
                    self.Channel2Quantity = edaqcomm.QuantityType.resistance

        elif channel == "C":
            if self.Channel3LinTherm.get() == "Thermistor":
                if self.Channel3Unit == "°C":
                    self.Channel3Quantity = edaqcomm.QuantityType.temp_celsius
                elif self.Channel3Unit == "K":
                    self.Channel3Quantity = edaqcomm.QuantityType.temp_kelvin
            elif self.Channel3LinTherm.get() == "Linear":
                if self.Channel3Typevar.get() == "voltage":
                    self.Channel3Quantity = edaqcomm.QuantityType.voltage
                if self.Channel3Typevar.get() == "resistor":
                    self.Channel3Quantity = edaqcomm.QuantityType.resistance

    def SaveA(self,savetofile):
        Root = minidom.Document()
        Stype = self.AddElementWAttr(Root,Root,"Sensor",{"type":self.Channel1LinTherm.get()},"")
        Sname = self.AddElement(Root,Stype,"Name",self.Channel1Name.get())
        
        Squantity = self.AddElement(Root,Stype,"Quantity",self.Channel1Quantityvar.get())
        Sunit = self.AddElement(Root,Stype,"Unit",self.Channel1Unit.get())

        #Here we check if we need to save as type thermistor or linear
        #Thermistor
        if dict(Stype.attributes.items())["type"] == "Thermistor":
            Scoefficient = self.AddElementWAttr(Root,Stype,"Coefficient",{"unit":"K"},self.Channel1BCoefficient)
            Sreference = self.AddElement(Root,Stype,"Reference","")
            Stemp = self.AddElementWAttr(Root,Sreference,"Temperature",{"unit":"K"},"298,15")
            Srefres = self.AddElementWAttr(Root,Sreference,"Resistance",{"unit":"Ω"},self.Channel1ReferenceRes)
            Sproberes = self.AddElementWAttr(Root,Stype,"ProbeResistance",{"unit":"Ω"},self.Channel1ProbeRes)

        #Linear
        else:
            Sintercept = self.AddElement(Root,Stype,"Intercept",self.Channel1Intercept)
            SSlope = self.AddElement(Root,Stype,"Slope",self.Channel1Slope)            
        xml_str = Root.toprettyxml(indent="\t")

        if savetofile:
            try:
                filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save file",filetypes=(("Xml File",".xml"),("All Files","*.*")))

                with open(filename,"w") as f:
                    f.write(xml_str)
            except:
                pass

        return Stype

    def SaveB(self,savetofile):
        Root = minidom.Document()
        Stype = self.AddElementWAttr(Root,Root,"Sensor",{"type":self.Channel2LinTherm.get()},"")
        Sname = self.AddElement(Root,Stype,"Name",self.Channel2Name.get())
        
        Squantity = self.AddElement(Root,Stype,"Quantity",self.Channel2Quantityvar.get())
        Sunit = self.AddElement(Root,Stype,"Unit",self.Channel2Unit.get())

        #Here we check if we need to save as type thermistor or linear
        #Thermistor
        if dict(Stype.attributes.items())["type"] == "Thermistor":
            Scoefficient = self.AddElementWAttr(Root,Stype,"Coefficient",{"unit":"K"},self.Channel2BCoefficient)
            Sreference = self.AddElement(Root,Stype,"Reference","")
            Stemp = self.AddElementWAttr(Root,Sreference,"Temperature",{"unit":"K"},"298,15")
            Srefres = self.AddElementWAttr(Root,Sreference,"Resistance",{"unit":"Ω"},self.Channel2ReferenceRes)
            Sproberes = self.AddElementWAttr(Root,Stype,"ProbeResistance",{"unit":"Ω"},self.Channel2ProbeRes)

        #Linear
        else:
            Sintercept = self.AddElement(Root,Stype,"Intercept",self.Channel2Intercept)
            SSlope = self.AddElement(Root,Stype,"Slope",self.Channel2Slope)            
        xml_str = Root.toprettyxml(indent="\t")

        if savetofile:
            try:
                filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save file",filetypes=(("Xml File",".xml"),("All Files","*.*")))

                with open(filename,"w") as f:
                    f.write(xml_str)
            except:
                pass
        return Stype

    def SaveC(self,savetofile):
        Root = minidom.Document()
        Stype = self.AddElementWAttr(Root,Root,"Sensor",{"type":self.Channel3LinTherm.get()},"")
        Sname = self.AddElement(Root,Stype,"Name",self.Channel3Name.get())
        
        Squantity = self.AddElement(Root,Stype,"Quantity",self.Channel3Quantityvar.get())
        Sunit = self.AddElement(Root,Stype,"Unit",self.Channel3Unit.get())

        #Here we check if we need to save as type thermistor or linear
        #Thermistor
        if dict(Stype.attributes.items())["type"] == "Thermistor":
            Scoefficient = self.AddElementWAttr(Root,Stype,"Coefficient",{"unit":"K"},self.Channel3BCoefficient)
            Sreference = self.AddElement(Root,Stype,"Reference","")
            Stemp = self.AddElementWAttr(Root,Sreference,"Temperature",{"unit":"K"},"298,15")
            Srefres = self.AddElementWAttr(Root,Sreference,"Resistance",{"unit":"Ω"},self.Channel3ReferenceRes)
            Sproberes = self.AddElementWAttr(Root,Stype,"ProbeResistance",{"unit":"Ω"},self.Channel3ProbeRes)

        #Linear
        else:
            Sintercept = self.AddElement(Root,Stype,"Intercept",self.Channel3Intercept)
            SSlope = self.AddElement(Root,Stype,"Slope",self.Channel3Slope)            
        xml_str = Root.toprettyxml(indent="\t")

        if savetofile:
            try:
                filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save file",filetypes=(("Xml File",".xml"),("All Files","*.*")))

                with open(filename,"w") as f:
                    f.write(xml_str)
            except:
                pass
        return Stype


    def SaveSettings(self):

        Root = minidom.Document()
        Measurements = self.AddElement(Root,Root,"Measurement","")
        Samplingfreq = self.AddElementWAttr(Root,Measurements,"SamplingFrequency",{"unit":"Hz"},self.samplingfreq)
        RefreshInterval = self.AddElementWAttr(Root,Measurements,"RefreshInterval",{"unit":"ms"},self.refreshrate.get())
        Averages = self.AddElement(Root,Measurements,"Averages",self.averaging)

        Xscale = self.AddElement(Root,Measurements,"XScale","")
        Title = self.AddElement(Root,Xscale,"Title",self.title.get())
        Points = self.AddElement(Root,Xscale,"Points",self.timeframepoints)

        Databuffer = self.AddElement(Root,Measurements,"DataBufferSize","100000") # Ez ötletem sincs mennyi kéne hogy legyen
        
        #Channel variables
        Channel1Settings = self.AddElement(Root,Measurements,"ChannelSettings","")
        Name1 = self.AddElement(Root,Channel1Settings,"Name","A")
        if "A" in self.ShownColumns:
            Active1 = self.AddElement(Root,Channel1Settings,"IsActive","True")
        else:
            Active1 = self.AddElement(Root,Channel1Settings,"IsActive","False")

        if self.automatic_scaleA.get():
            Autocsale1 = self.AddElement(Root,Channel1Settings,"IsAutoscaled","True")
        else:
            Autocsale1 = self.AddElement(Root,Channel1Settings,"IsAutoscaled","False")
        Ymin1 = self.AddElement(Root,Channel1Settings,"YMin",self.ylimitAbot)
        Ymax1 = self.AddElement(Root,Channel1Settings,"YMax",self.ylimitAtop)
        rgb1 = [int(self.line1Color[i+1:i+3],16) for i in range(0,5,2)]
        color1 = self.AddElementWAttr(Root,Channel1Settings,"Colour",{"description":"Colour [R={}, G={}, B={}]".format(rgb1[0],rgb1[1],rgb1[2])},"")
        sensorinterface = self.AddElementWAttr(Root,Channel1Settings,"SensorInterfacing",{"label":self.Channel1Typevar.get()},self.Channel1Type)

        #Sensor settings
        sensora = self.SaveA(False)
        Channel1Settings.appendChild(sensora)

        #Levelcrossing variables
        objlen1 = self.AddElement(Root,Channel1Settings,"ObjectLength",self.LevelCrossingObjLenA)
        levelcrossing1 = self.AddElement(Root,Channel1Settings,"LevelCrossingDetector","")
        lclevel1 = self.AddElement(Root,levelcrossing1,"Level",self.LevelCrossingLevelA)
        lchyst1 = self.AddElement(Root,levelcrossing1,"Hysteresis",self.LevelCrossingHystA)
        if self.LevelcrossingonA.get():
            lcactive1 = self.AddElement(Root,levelcrossing1,"IsActive","True")
        else:
            lcactive1 = self.AddElement(Root,levelcrossing1,"IsActive","False")


        Channel2Settings = self.AddElement(Root,Measurements,"ChannelSettings","")
        Name2 = self.AddElement(Root,Channel2Settings,"Name","B")
        if "B" in self.ShownColumns:
            Active2 = self.AddElement(Root,Channel2Settings,"IsActive","True")
        else:
            Active2 = self.AddElement(Root,Channel2Settings,"IsActive","False")

        if self.automatic_scaleB.get():
            Autocsale2 = self.AddElement(Root,Channel2Settings,"IsAutoscaled","True")
        else:
            Autocsale2 = self.AddElement(Root,Channel2Settings,"IsAutoscaled","False")
        Ymin2 = self.AddElement(Root,Channel2Settings,"YMin",self.ylimitBbot)
        Ymax2 = self.AddElement(Root,Channel2Settings,"YMax",self.ylimitBtop)
        rgb2 = [int(self.line2Color[i+1:i+3],26) for i in range(0,5,2)]
        color2 = self.AddElementWAttr(Root,Channel2Settings,"Colour",{"description":"Colour [R={}, G={}, B={}]".format(rgb2[0],rgb2[1],rgb2[2])},"")
        sensorinterface = self.AddElementWAttr(Root,Channel2Settings,"SensorInterfacing",{"label":self.Channel2Typevar.get()},self.Channel2Type)

        sensorb = self.SaveB(False)
        Channel2Settings.appendChild(sensorb)

        objlen2 = self.AddElement(Root,Channel2Settings,"ObjectLength",self.LevelCrossingObjLenB)
        levelcrossing2 = self.AddElement(Root,Channel2Settings,"LevelCrossingDetector","")
        lclevel2 = self.AddElement(Root,levelcrossing2,"Level",self.LevelCrossingLevelB)
        lchyst2 = self.AddElement(Root,levelcrossing2,"Hysteresis",self.LevelCrossingHystB)
        if self.LevelcrossingonB.get():
            lcactive2 = self.AddElement(Root,levelcrossing2,"IsActive","True")
        else:
            lcactive2 = self.AddElement(Root,levelcrossing2,"IsActive","False")



        Channel3Settings = self.AddElement(Root,Measurements,"ChannelSettings","")
        Name3 = self.AddElement(Root,Channel3Settings,"Name","C")
        if "C" in self.ShownColumns:
            Active3 = self.AddElement(Root,Channel3Settings,"IsActive","True")
        else:
            Active3 = self.AddElement(Root,Channel3Settings,"IsActive","False")

        if self.automatic_scaleC.get():
            Autocsale3 = self.AddElement(Root,Channel3Settings,"IsAutoscaled","True")
        else:
            Autocsale3 = self.AddElement(Root,Channel3Settings,"IsAutoscaled","False")
        Ymin3 = self.AddElement(Root,Channel3Settings,"YMin",self.ylimitCbot)
        Ymax3 = self.AddElement(Root,Channel3Settings,"YMax",self.ylimitCtop)
        rgb3 = [int(self.line3Color[i+1:i+3],36) for i in range(0,5,2)]
        color3 = self.AddElementWAttr(Root,Channel3Settings,"Colour",{"description":"Colour [R={}, G={}, B={}]".format(rgb3[0],rgb3[1],rgb3[2])},"")
        sensorinterface = self.AddElementWAttr(Root,Channel3Settings,"SensorInterfacing",{"label":self.Channel3Typevar.get()},self.Channel3Type)

        sensorc = self.SaveC(False)
        Channel3Settings.appendChild(sensorc)

        objlen3 = self.AddElement(Root,Channel3Settings,"ObjectLength",self.LevelCrossingObjLenC)
        levelcrossing3 = self.AddElement(Root,Channel3Settings,"LevelCrossingDetector","")
        lclevel3 = self.AddElement(Root,levelcrossing3,"Level",self.LevelCrossingLevelC)
        lchyst3 = self.AddElement(Root,levelcrossing3,"Hysteresis",self.LevelCrossingHystC)
        if self.LevelcrossingonC.get():
            lcactive3 = self.AddElement(Root,levelcrossing3,"IsActive","True")
        else:
            lcactive3 = self.AddElement(Root,levelcrossing3,"IsActive","False")


        '''
        sensorb = self.SaveB(False)
        sensorc = self.SaveC(False)
        
        Measurements.appendChild(sensorb)
        Measurements.appendChild(sensorc)'''
        try:
            filename = filedialog.asksaveasfilename(initialdir=path.curdir,title="Save file",filetypes=(("Xml File",".xml"),("All Files","*.*")))
            xml_str = Root.toprettyxml(indent="\t")
            with open(filename,"w") as f:
                f.write(xml_str)
        except:
            pass


    def LoadSettingsA(self,file="input"):
        if file=="input":
            try:
                openfilename = filedialog.askopenfilename(initialdir=path.curdir,title="lets open a file",filetypes=(("Xml File",".xml"),("All Files","*.*")))
                tree = ET.parse(openfilename)
            except:
                return None
        else:
            tree = ET.ElementTree(ET.fromstring(file))
        Root = tree.getroot()
        
        data = dict()

        for i in Root:
            data[i.tag] = [i.attrib,i.text]
        
        for i in data:
            if data[i][1] == None:
                data[i][1] = ""
        self.Channel1Name.set(data["Name"][1])
        self.Channel1Quantityvar.set(data["Quantity"][1])
        
        if Root.attrib["type"] == "Linear":
            self.Channel1LinTherm.set("Linear")
            self.Channel1Intercept = float(data["Intercept"][1])
            self.Channel1Slope = float(data["Slope"][1])
            
        elif Root.attrib["type"] == "Thermistor":
            self.Channel1LinTherm.set("Thermistor")
            for i in Root.find("Reference"):
                data[i.tag] = [i.attrib,i.text]
            self.Channel1BCoefficient = int(data["Coefficient"][1])
            self.Channel1ReferenceRes = int(data["Resistance"][1])
            self.Channel1ProbeRes = int(data["ProbeResistance"][1])
        self.Channel1Unit.set(data["Unit"][1])
        self.Setquantity("A")

    def LoadSettingsB(self,file="input"):
        if file=="input":
            try:
                openfilename = filedialog.askopenfilename(initialdir=path.curdir,title="lets open a file",filetypes=(("Xml File",".xml"),("All Files","*.*")))
                tree = ET.parse(openfilename)
            except:
                return None
        else:
            tree = ET.ElementTree(ET.fromstring(file))
        Root = tree.getroot()
        
        data = dict()

        for i in Root:
            data[i.tag] = [i.attrib,i.text]
        
        for i in data:
            if data[i][1] == None:
                data[i][1] = ""
        self.Channel2Name.set(data["Name"][1])
        self.Channel2Quantityvar.set(data["Quantity"][1])
        
        if Root.attrib["type"] == "Linear":
            self.Channel2LinTherm.set("Linear")
            self.Channel2Intercept = float(data["Intercept"][1])
            self.Channel2Slope = float(data["Slope"][1])
            
        elif Root.attrib["type"] == "Thermistor":
            self.Channel2LinTherm.set("Thermistor")
            for i in Root.find("Reference"):
                data[i.tag] = [i.attrib,i.text]
            self.Channel2BCoefficient = int(data["Coefficient"][1])
            self.Channel2ReferenceRes = int(data["Resistance"][1])
            self.Channel2ProbeRes = int(data["ProbeResistance"][1])
        self.Channel2Unit.set(data["Unit"][1])
        self.Setquantity("B")

    def LoadSettingsC(self,file="input"):
        if file=="input":
            try:
                openfilename = filedialog.askopenfilename(initialdir=path.curdir,title="lets open a file",filetypes=(("Xml File",".xml"),("All Files","*.*")))
                tree = ET.parse(openfilename)
            except:
                return None
        else:
            tree = ET.ElementTree(ET.fromstring(file))
        Root = tree.getroot()
        
        data = dict()

        for i in Root:
            data[i.tag] = [i.attrib,i.text]
        
        for i in data:
            if data[i][1] == None:
                data[i][1] = ""
        self.Channel3Name.set(data["Name"][1])
        self.Channel3Quantityvar.set(data["Quantity"][1])
        
        
        if Root.attrib["type"] == "Linear":
            self.Channel3LinTherm.set("Linear")
            self.Channel3Intercept = float(data["Intercept"][1])
            self.Channel3Slope = float(data["Slope"][1])
            
        elif Root.attrib["type"] == "Thermistor":
            self.Channel3LinTherm.set("Thermistor")
            for i in Root.find("Reference"):
                data[i.tag] = [i.attrib,i.text]
            self.Channel3BCoefficient = int(data["Coefficient"][1])
            self.Channel3ReferenceRes = int(data["Resistance"][1])
            self.Channel3ProbeRes = int(data["ProbeResistance"][1])
        self.Channel3Unit.set(data["Unit"][1])
        self.Setquantity("C")

    def LoadSettings(self):
        try:
            openfilename = filedialog.askopenfilename(initialdir=path.curdir,title="lets open a file",filetypes=(("Xml File",".xml"),("All Files","*.*")))
            tree = ET.parse(openfilename)
        except:
            return None
        Root = tree.getroot()

        data = dict()

        for i in Root:
            data[i.tag] = [i.attrib,i.text]
        
        self.samplingfreq = float(data["SamplingFrequency"][1])
        self.samplingfreqval.set(self.samplingfreq)

        self.refreshrate.set(float(data["RefreshInterval"][1]))

        self.averaging = int(data["Averages"][1])
        self.SetAveragingvar()

        for i in Root.find("XScale"):
            data[i.tag] = [i.attrib,i.text]


        self.title.set(data["Title"][1])
        self.timeframepoints = int(data["Points"][1])
        self.timeframepointsvar.set(self.timeframepoints)

        return(tree)


    def LoadSetup(self,file="input"):
        if file=="input":
            try:
                openfilename = filedialog.askopenfilename(initialdir=path.curdir,title="lets open a file",filetypes=(("Xml File",".xml"),("All Files","*.*")))
                tree = ET.parse(openfilename)
            except:
                return None
        else:
            tree = file
        Root = tree.getroot()
        
        curchannel = 1

        sensornodes = []
        for i in Root.findall("ChannelSettings"):
            sensornodes.append(i.find("Sensor"))


        for i in Root.findall("ChannelSettings"):
            curdata = dict()
            for j in i:
                curdata[j.tag] = [j.attrib,j.text]
            
            if curchannel == 1:

                if curdata["IsAutoscaled"][1] == "True":
                    self.automatic_scaleA.set(1)
                elif curdata["IsAutoscaled"][1] == "False":
                    self.automatic_scaleA.set(0)

                self.ylimitAbot = float(curdata["YMin"][1])
                self.ylimitAbotvar.set(self.ylimitAbot)

                self.ylimitAtop = float(curdata["YMax"][1])
                self.ylimitAtopvar.set(self.ylimitAtop)

                colorstring = curdata["Colour"][0]["description"]
                colorlist = [x.split("=")[-1] for x in colorstring.split(",")]
                colorlist = [int(x.split("]")[0]) for x in colorlist]
                newcolor = "#%02x%02x%02x" % (colorlist[0],colorlist[1],colorlist[2])
                self.line1Color = newcolor

                self.Channel1Type = int(curdata["SensorInterfacing"][1])
                self.Channel1Typevar.set(curdata["SensorInterfacing"][0]["label"])
                
                self.LoadSettingsA(ET.tostring(sensornodes[0],encoding="utf-8",method="xml"))

                self.LevelCrossingObjLenA = float(curdata["ObjectLength"][1])
                self.LevelCrossingObjLenAvar.set(self.LevelCrossingObjLenA)
                
                for k in i.find("LevelCrossingDetector"):
                    curdata[k.tag] = [k.attrib,k.text]

                self.LevelCrossingLevelA = float(curdata['Level'][1])
                self.LevelCrossingLevelAvar.set(self.LevelCrossingLevelA)

                self.LevelCrossingHystA = float(curdata['Hysteresis'][1])
                self.LevelCrossingHystAvar.set(self.LevelCrossingHystA)

                if curdata["IsActive"][1] == "True":
                    self.LevelcrossingonA.set(1)
                else:
                    self.LevelcrossingonA.set(0)

            if curchannel == 2:

                if curdata["IsAutoscaled"][1] == "True":
                    self.automatic_scaleB.set(1)
                elif curdata["IsAutoscaled"][1] == "False":
                    self.automatic_scaleB.set(0)

                self.ylimitBbot = float(curdata["YMin"][1])
                self.ylimitBbotvar.set(self.ylimitBbot)

                self.ylimitBtop = float(curdata["YMax"][1])
                self.ylimitBtopvar.set(self.ylimitBtop)

                colorstring = curdata["Colour"][0]["description"]
                colorlist = [x.split("=")[-1] for x in colorstring.split(",")]
                colorlist = [int(x.split("]")[0]) for x in colorlist]
                newcolor = "#%02x%02x%02x" % (colorlist[0],colorlist[1],colorlist[2])
                self.line2Color = newcolor

                self.Channel2Type = int(curdata["SensorInterfacing"][1])
                self.Channel2Typevar.set(curdata["SensorInterfacing"][0]["label"])
                
                self.LoadSettingsB(ET.tostring(sensornodes[1],encoding="utf-8",method="xml"))

                self.LevelCrossingObjLenB = float(curdata["ObjectLength"][1])
                self.LevelCrossingObjLenBvar.set(self.LevelCrossingObjLenB)
                
                for k in i.find("LevelCrossingDetector"):
                    curdata[k.tag] = [k.attrib,k.text]

                self.LevelCrossingLevelB = float(curdata['Level'][1])
                self.LevelCrossingLevelBvar.set(self.LevelCrossingLevelB)

                self.LevelCrossingHystB = float(curdata['Hysteresis'][1])
                self.LevelCrossingHystBvar.set(self.LevelCrossingHystB)

                if curdata["IsActive"][1] == "True":
                    self.LevelcrossingonB.set(1)
                else:
                    self.LevelcrossingonB.set(0)

            if curchannel == 3:

                if curdata["IsAutoscaled"][1] == "True":
                    self.automatic_scaleC.set(1)
                elif curdata["IsAutoscaled"][1] == "False":
                    self.automatic_scaleC.set(0)

                self.ylimitCbot = float(curdata["YMin"][1])
                self.ylimitCbotvar.set(self.ylimitCbot)

                self.ylimitCtop = float(curdata["YMax"][1])
                self.ylimitCtopvar.set(self.ylimitCtop)

                colorstring = curdata["Colour"][0]["description"]
                colorlist = [x.split("=")[-1] for x in colorstring.split(",")]
                colorlist = [int(x.split("]")[0]) for x in colorlist]
                newcolor = "#%02x%02x%02x" % (colorlist[0],colorlist[1],colorlist[2])
                self.line3Color = newcolor

                self.Channel3Type = int(curdata["SensorInterfacing"][1])
                self.Channel3Typevar.set(curdata["SensorInterfacing"][0]["label"])
                
                self.LoadSettingsC(ET.tostring(sensornodes[2],encoding="utf-8",method="xml"))

                self.LevelCrossingObjLenC = float(curdata["ObjectLength"][1])
                self.LevelCrossingObjLenCvar.set(self.LevelCrossingObjLenC)
                
                for k in i.find("LevelCrossingDetector"):
                    curdata[k.tag] = [k.attrib,k.text]

                self.LevelCrossingLevelC = float(curdata['Level'][1])
                self.LevelCrossingLevelCvar.set(self.LevelCrossingLevelC)

                self.LevelCrossingHystC = float(curdata['Hysteresis'][1])
                self.LevelCrossingHystCvar.set(self.LevelCrossingHystC)

                if curdata["IsActive"][1] == "True":
                    self.LevelcrossingonC.set(1)
                else:
                    self.LevelcrossingonC.set(0)

            curchannel += 1
        



        
if __name__ == "__main__":
    a = Settings()
    a.LoadSettings()