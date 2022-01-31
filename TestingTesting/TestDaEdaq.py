from time import time
from numpy import where
import serial
from serial import Serial
import time

ser = Serial(port="/dev/ttyUSB0", baudrate=230400, timeout=1,
        bytesize=8, parity=serial.PARITY_NONE, stopbits=1)


def sendAndReceive(send):
        send2 = bytes(send,'utf-8')
        ser.write(send2)
        received = ser.read(1)
        try:
            if received != send2:
                print("Meghibásodott a(z) "+send+" üzenet")
            return received
        except:
            print("Nem kaptunk üzenetet :(")

def startContSampling():
        sendAndReceive("@")
        sendAndReceive("S")

def setSamplingFreq(sampling_freq):
        sendAndReceive("@")
        sendAndReceive("f")
        c = 0
        c = sendAndReceive(chr(c))
        sampling_freq *= 3
        c = int(sampling_freq / 256)
        c = sendAndReceive(chr(c))
        c = sampling_freq % 256
        c = sendAndReceive(chr(c))

def fillArrayContSampling(count):
    data = [[],[],[]]
    for i in range(0, count): 
        for j in range(0, 3):
                c = ser.read(1)
                data[j].append(ord(c) * 256)
                c = ser.read(1)
                data[j][i] += ord(c)
    return data

def stopContSampling():
    c = 27     #ESC
    ser.write(c.to_bytes(1,"big"))
    time.sleep(0.01)
    ser.flushOutput()
    ser.flushInput()

def flushBuffers():
    ser.flushOutput()
    ser.flushInput()


setSamplingFreq(1000)
flushBuffers()
startContSampling()

for i in range(1000):
    start = time.time()
    data = []
    for i in range(0, 3):
        c = ser.read(1)
        data.append(ord(c) * 256)
        c = ser.read(1)
        data[i] += ord(c)
    print(1/(time.time()-start))


stopContSampling()

'''

data = []
sendAndReceive("@")
sendAndReceive("M")
sendAndReceive("#")


for i in range(0, 3):
    c = ser.read();
    print(c.split())
    data.append(ord(c) * 256);
    c = ser.read(3);
    data[i] += ord(c);
print(data)

'''