import os
import serial
ser = serial.Serial('COM18')
line = []
temp = []
weakfluxc=10
voltc=0
ampec=0
count=0
# while True:
#     votol=ser.read()
#     print(votol.decode('utf-16-le'))
while True:
    for c in ser.read():
        line.append(hex(c))
        count = count + 1
        if count == 17:
            weakfluxc = int(c)
        if count == 18:
            a = format(c, '#02x')
        if count == 19:
            voltc = int(a+format(c, '02x'),16)
        if count == 20:
            b = c
        if count == 21:
            voltc = int((b<<8)|c)
        if hex(c) == '0xd':
            #print(line)
            print(f'VoltageCalib:{voltc};AmpeCalib:{ampec};WkFlxCalib:{weakfluxc}')
            count = 0
            line = []