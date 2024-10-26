import os
import serial
import time 
ser = serial.Serial('COM18')
msg = ''
switch = 'No'
line = []
exi = False
gear = ''
state = ''
weakfluxc=0
throttle=0
voltc=0
ampec=0
count=0
def bxor(a, b):
    result_int = int.from_bytes(a, byteorder="big") ^ int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")
def trans():
    header = b'\xc0\x14\x0d\x59\x42'
    headersum = b'\xC2'
    voltd=960
    ampeq=2000
    rpm=9999
    fault= b'\x00\x00\x00\x00'
    ictemp= 25 + 50
    motemp=100 + 50
    tempcof=2008
    fustatus=b'\x80'
    icstatus=b'\x03'
    checksum = bxor(bxor(bxor(bxor(bxor(bxor(bxor(bxor(bxor(headersum,voltd.to_bytes(2)),ampeq.to_bytes(2)),fault),rpm.to_bytes(2)),ictemp.to_bytes(2)),motemp.to_bytes(2)),tempcof.to_bytes(2)),fustatus),icstatus)
    #checksum = header ^ voltd.to_bytes(2) ^ ampeq.to_bytes(2) ^ fault ^ rpm.to_bytes(2) ^ ictemp.to_bytes(2) ^ motemp.to_bytes(2) ^ tempcof.to_bytes(2) ^ fustatus ^ icstatus
    print(checksum)
    ser.write(header + voltd.to_bytes(2) + ampeq.to_bytes(2) + fault + rpm.to_bytes(2) + ictemp.to_bytes(2) + motemp.to_bytes(2) + tempcof.to_bytes(2) + fustatus + icstatus + checksum + b'\x0d')
    #ser.write(b"\xc0\x14\x0d\x59\x42\x02\x14\x00\x0f\x01\x00\x00\x00\x00\x02\xb8\x5d\x4b\x22\xd6\x80\x03\x01\x0d")
    
def connect():
    ser.write(b'\xC0\x14\x05\x52\x01\x14\x02\x03\x7F\x02\x94\x0A\x00\x32\x23\x28\x02\x76\x04\x5F\x00\x71\x13\x0D') #page1
    ser.write(b'\xC0\x14\x05\x52\x02\x00\x1E\x3C\x50\x5F\x0F\xA0\x23\x28\x17\x70\xA5\x2A\x0C\x1E\x1E\x0F\xE3\x0D')
    ser.write(b'\xC0\x14\x05\x52\x03\x00\x1E\x50\x64\x69\x04\x1A\x00\x14\x24\xD4\x0A\x30\x18\x16\xE9\x71\x95\x0D') #version + page 3
    ser.write(b'\xC0\x14\x05\x52\x04\x06\x0C\xCC\x01\x40\x04\xB0\x5C\x5C\x05\x01\xF4\x17\x70\x00\x00\x03\x20\x0D')
    ser.write(b'\xC0\x14\x05\x52\x05\xC0\x01\xC0\x00\xC0\x00\xC0\x00\xC0\x11\xC0\x05\xC0\x07\xC0\x08\x03\x9F\x0D')
    ser.write(b'\xC0\x14\x05\x52\x06\xC0\x09\xC0\x8A\xC0\x0B\xC0\x00\xC0\x00\xC0\x15\xC0\x0F\xC8\x92\x71\xFC\x0D')
    ser.write(b'\xC0\x14\x05\x52\x07\x39\xC7\x0D\xE0\x50\xFA\x00\x00\x00\x00\x27\x02\x76\x04\x5D\x00\x71\x46\x0D')

while not exi:
    for c in ser.read():
        line.append(hex(c))
        count = count + 1
        if count >= 4 and count <= 10:
            msg+=(chr(c))
        if count == 13:
            if format(c, '02x') == '55':
                mode="REMOTE"
            else:
                mode="LOCAL"
        if count == 14:
            d = format(c, '#02x')
        if count == 15:
            throttle = "{:.2f}".format(int(d+format(c, '02x'),16)/5945)
        if count == 16:
            signals=format(c, '02x')
            leftsig=signals[:1]
            rigtsig=signals[1:]
            switch = 'No'
            if leftsig == 'e' or leftsig == 'f':
                state = 'BRL'
                if leftsig == 'f':
                    switch = 'AxisV'
            if leftsig == 'c' or leftsig == 'd':
                state = 'BR'
                if leftsig == 'd':
                    switch = 'AxisV'
            if leftsig == 'a' or leftsig == 'b':
                state = 'BL'
                if leftsig == 'b':
                    switch = 'AxisV'
            if leftsig == '6' or leftsig == '7':
                state = 'RL'
                if leftsig == '7':
                    switch = 'AxisV'
            if leftsig == '8' or leftsig == '9':
                state = 'B'
                if leftsig == '9':
                    switch = 'AxisV'
            if leftsig == '4' or leftsig == '5':
                state = 'R'
                if leftsig == '5':
                    switch = 'AxisV'
            if leftsig == '2' or leftsig == '3':
                state = 'L'
                if leftsig == '3':
                    switch = 'AxisV'
            if leftsig == '0' or leftsig == '1':
                state = 'None'
                if leftsig == '1':
                    switch = 'AxisV'
            if rigtsig == '0' or rigtsig == '8':
                gear = 'L'
                if rigtsig == '8':
                    switch = 'AxisA'
            if rigtsig == '1' or rigtsig == '9':
                gear = 'M'
                if rigtsig == '9':
                    switch = 'AxisA'
            if rigtsig == '2' or rigtsig == 'a':
                gear = 'H'
                if rigtsig == 'a':
                    switch = 'AxisA'
            if rigtsig == '3' or rigtsig == 'b':
                gear = 'S'
                if rigtsig == 'b':
                    switch = 'AxisA'
        if count == 17:
            weakfluxc = int(c)
        if count == 19:
            a = format(c, '#02x')
        if count == 20:
            voltc = int(a+format(c, '02x'),16)
        if count == 21:
            b = format(c, '#02x')
        if count == 22:
            ampec = int(b+format(c, '02x'),16)
        if hex(c) == '0xd':
            #print(line)
            
            print(f'Switch:{switch} Mode:{mode} Gear:{gear} State:{state} VoltageCalib:{voltc} AmpeCalib:{ampec} WkFlxCalib:{weakfluxc} Throttle:{throttle}v MSG:{msg}')
            if msg[:5] == "LDGET":
                print("CONNECT COMMAND")
                time.sleep(0.5)
                connect()
            elif msg[:5] == "RESET":
                print("RESET COMMAND")
                ser.close()
                exi = True
            else:
                trans()
            count = 0
            line = []
            msg = ''


