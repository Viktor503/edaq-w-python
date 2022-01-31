'''
Created on 2014.03.27.
Python module to use the Edaq530 data acquisition device

'''
from numpy import unicode_
import serial
from serial import Serial
import math
import sys
import time

ADC_RES = 0.001220703
PULLUP_RESISTANCE = 10000
THERM_R_25 = 10000
THERM_B = 3977

'''
Converts A/D converter code to voltage
'''
def adcCodeToVoltage(d):
    return d * ADC_RES

'''
Converts A/D converter code to voltage, and the voltage to resistance
'''
def adcCodeToResistance(d):
    u = adcCodeToVoltage(d)
    u /= 5.0
    return u * (PULLUP_RESISTANCE / (1.0 - u))

'''
Converts A/D converter code to temperature in Kelvin (Thermistor resistance)
'''
def adcCodeToTempKelvin(d):
    r = adcCodeToResistance(d)
    return 1.0 / ((1.0 / 298.16) + ((1.0 / THERM_B) * math.log(r / THERM_R_25)))

'''
Converts A/D converter code to temperature in Celsius (Thermistor resistance)
'''
def adcCodeToTempCelsius(d):
    return adcCodeToTempKelvin(d) - 273.16

'''
Converts the adc code to the measured quantity, using QuantityType
'''
def getMeasuredQuantity(d, type):
    if type == QuantityType.voltage:
        return adcCodeToVoltage(d)
    elif type == QuantityType.resistance:
        return adcCodeToResistance(d)
    elif type == QuantityType.temp_kelvin:
        return adcCodeToTempKelvin(d)
    elif type == QuantityType.temp_celsius:
        return adcCodeToTempCelsius(d)
    else:
        return adcCodeToVoltage(d)


'''
Class for Edaq530 measurements
'''
class Edaq530Comm:
    
    def __init__(self, name):
        self.name = name
    
    '''
    Connect to the device
    '''
    def connect(self):
        self.ser = Serial(port=self.name, baudrate=230400, timeout=1,
        bytesize=8, parity=serial.PARITY_NONE, stopbits=1)
        self.ser.readline()
    
    '''
    Sends a character to the device. The device should answer by sending 
    back the same character, so we check if the sent character equals
    the received character.
    '''

    def sendAndReceive(self, send):
        send2 = bytes(send,'utf-8')
        self.ser.write(send2)
        received = self.ser.read(1)
        try:
            if received != send2:
                raise WrongCharReceivedError(send2, received)
            return received
        except WrongCharReceivedError as e:
            print(e.msg)
            print("The program stops sampling, disconnects the device and exit...")
            self.stopContSampling()
            self.disconnect()
            sys.exit(1)
            
            
            
    '''        
    Sends a character to the device. The equality of the sent and the
    received characters is not checked.
    '''
    def sendAndReceiveNoCheck(self, send):
        self.ser.write(send)
        received = self.ser.read(1)
        return received
        
        
    '''
    Sends  the '@I' identification command, adn reads the identification
    string of the device.    
    '''
    def getID(self):
        self.sendAndReceive("@")
        self.sendAndReceive("I")
        s = "a"
        msg = ""
        while s != "#":
            s = self.sendAndReceiveNoCheck("#")
            if s != "#":
                msg += s
        return msg
    
    '''    
    Returns the code used to set the input channel types.    
    '''
    def getChannelSource(self, ch):
        if ch == ChannelType.voltage or ch == ChannelType.resistor:
            return chr(0)
        elif ch == ChannelType.inamp:
            return chr(1)
        elif ch == ChannelType.photo:
            return chr(2)
        else:
            return chr(0)
    
    '''
    Sets the input channels of the device, using ChannelType
    '''
    def setInputs(self, ch_a, ch_b, ch_c):
        self.sendAndReceive("@")
        self.sendAndReceive("C")
        self.sendAndReceive(self.getChannelSource(ch_a))
        self.sendAndReceive(self.getChannelSource(ch_b))
        self.sendAndReceive(self.getChannelSource(ch_c))
        
        self.sendAndReceive("@")
        self.sendAndReceive("E")
        if ch_a == ChannelType.photo or ch_b == ChannelType.photo or ch_c == ChannelType.photo:
            self.sendAndReceive(chr(1))
            print("kukiiiiiiiii")
        else:
            self.sendAndReceive(chr(0))

	# Turn on pull up resistors if measuring resistance
        self.sendAndReceive("@")
        self.sendAndReceive("P")
        c = 0;
        if ch_a != ChannelType.resistor:
            c += 1
        if ch_b != ChannelType.resistor:
            c += 2
        if ch_c != ChannelType.resistor:
            c += 4
        self.sendAndReceive(chr(c))
        
        
    '''
    Sets the sampling frequency of the device.  
    11<=sampling_freq<=1000, 3 channels
    '''
    def setSamplingFreq(self, sampling_freq):
            self.sendAndReceive("@")
            self.sendAndReceive("f")
            c = 0
            c = self.sendAndReceive(chr(c))
            sampling_freq *= 3
            c = int(sampling_freq / 256)
            c = self.sendAndReceive(chr(c))
            c = sampling_freq % 256
            c = self.sendAndReceive(chr(c))
     
    '''
    Sends the '@S' continous measurement command to the device.
    The measured data can be read using functions fillArrayContsampling and
    fillArrayContiSamplingOneCh.
    Use stopContSampling() to stop sampling.       
    '''
    def startContSampling(self):
            self.sendAndReceive("@")
            self.sendAndReceive("S")
    
    '''
    Returns an array with count samples of the given channel.  
    Start countinous sampling by startContSampling() befora calling this function.    
    The measured A/D converter code can be converted to the desired quantity
    using the function getMeasuredQuantity.   
    '''
    def fillArrayContSamplingOneCh(self, channel_no, count):
        data = []
        for i in range(0, count):
            for j in range(0,3):
                if (j == channel_no):
                        c = self.ser.read(1)
                        data.append(ord(c) * 256)
                        c = self.ser.read(1)
                        data[i] += ord(c)
                else:
                    for k in range(0, 2):
                            self.ser.read(1)
        return data
        	
      
    '''
    Returns a two dimensional array with count samples from all 3 channels. 
    Start countinous sampling by startContSampling() befora calling this function. 
    The measured A/D converter code can be converted to the desired quantity
    using the function getMeasuredQuantity.         
    '''
    def fillArrayContSampling(self, count):
        data = [[],[],[]]
        for i in range(0, count): 
            for j in range(0, 3):
                    c = self.ser.read(1)
                    data[j].append(ord(c) * 256)
                    c = self.ser.read(1)
                    data[j][i] += ord(c)
        return data
       	
    '''
    Stops continous sampling and flushs the buffers.    
    '''
    def stopContSampling(self):
        c = 27     #ESC
        self.ser.write(c.to_bytes(1,"big"))
        #time.sleep(0.01)
        self.ser.flushOutput()
        self.ser.flushInput()
        
    def flushBuffers(self):
        self.ser.flushOutput()
        self.ser.flushInput()
      
    '''
    Measure one sample on all 3 channles. The measured data is returned
    in an array of 3 elements. 
    The measured A/D converter code can be converted to the desired quantity
    using the function getMeasuredQuantity.        
    '''
    def measure(self):
        self.sendAndReceive("@")
        self.sendAndReceive("M")
        self.sendAndReceive("#")
        data = []
        for i in range(0, 3):
            c = self.ser.read(1);
            data.append(ord(c) * 256);
            c = self.ser.read(1);
            data[i] += ord(c);
        return data

    def measureWithoutChecking(self):
        data = []
        for i in range(0, 3):
            c = self.ser.read(1);
            data.append(ord(c) * 256);
            c = self.ser.read(1);
            data[i] += ord(c);
        return data
    
    '''  
    Disconnects the device    
    '''
    def disconnect(self):
        self.ser.close()
       
        
'''
Channel type constatnts        
'''
class ChannelType:
    voltage = 0
    resistor = 1
    inamp = 2
    photo = 3
    
'''
Quantity type constants    
'''
class QuantityType:
    voltage = 0
    resistance = 1
    temp_kelvin = 2
    temp_celsius = 3

'''
Raised if wrong char received from the device
'''        
class WrongCharReceivedError(Exception):
    def __init__(self, sent, received):
        self.msg = received + " (" + str(ord(received)) + ") received instead of " + sent + " (" + str(ord(sent)) + ")"
        

