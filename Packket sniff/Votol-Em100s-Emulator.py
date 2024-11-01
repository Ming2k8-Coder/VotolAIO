import os
import serial
import time 
from pathlib import Path
ROOT_DIR = Path(__file__).parent
TEXT_FILE = ROOT_DIR / 'VotolParamemu.txt'

#Const Variable---------------
ser = serial.Serial('COM18')
sendheader=b'\xC0\x14' # Controller sending
respone1byte=b'\x0D'
responemultibyte=b'\x05'
votolRbyte=b'R'
#Volatile Variable------------
msg = ''
throttle = 0
switch = 'No'
mode = 'LOCAL'
exi = False
weakfluxc=0
throttle=0
voltc=0
ampec=0
count=0
fustatus=b'\x88'
icstatus=b'\x03'
# ------------------------------
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
def crc16(buffer):
    checksum = 0
    # print(buffer)
    for i in buffer:
        checksum = checksum ^ i
    checksum=checksum.to_bytes(1)
    # print(checksum)
    return checksum
def transmitDisp():
    global icstatus
    header = sendheader + respone1byte + b'\x59\x42'
    voltd=int(map_range(float(throttle),0.77,4.60,1200,1123))
    ampeq=int(map_range(float(throttle),0.77,4.60,5,5400))
    if ampeq < 0: ampeq = 0
    rpm=int(map_range(float(throttle),0.77,4.60,0,9000))
    if rpm <= 0:
        icstatus=b'\x00'
        rpm=0
    unknownbit=b'\x01'
    fault= b'\x00\x00\x00\x00'
    ictemp= 40 + 50
    motemp=67 + 50
    tempcof= 8000
    buffer = header + voltd.to_bytes(2) + ampeq.to_bytes(2) +unknownbit+ fault + rpm.to_bytes(2) + ictemp.to_bytes(1) + motemp.to_bytes(1) + tempcof.to_bytes(2) + fustatus + icstatus
    checksum = crc16(buffer)
    ser.write(buffer + checksum + b'\x0d')
    #ser.write(b"\xc0\x14\x0d\x59\x42\x02\x14\x00\x0f\x01\x00\x00\x00\x00\x02\xb8\x5d\x4b\x22\xd6\x80\x03\x01\x0d")
    
def connect():
    try:
        f = open(TEXT_FILE)
    except:
        print("ParamFile not found,please write to emulator first")
        return
    paramfile = f.readlines()
    f.close()
    packet1send(paramfile)
    packet2send(paramfile)
    packet3send(paramfile)
    packet4send(paramfile)
    #ser.write(b'\xC0\x14\x05\x52\x04\x06\x0C\xCC\x01\x40\x04\xB0\x5C\x5C\x05\x01\xF4\x17\x70\x00\x00\x03\x20\x0D')
    ser.write(b'\xC0\x14\x05\x52\x05\xC0\x01\xC0\x00\xC0\x00\xC0\x00\xC0\x11\xC0\x05\xC0\x07\xC0\x08\x03\x9F\x0D')
    ser.write(b'\xC0\x14\x05\x52\x06\xC0\x09\xC0\x8A\xC0\x0B\xC0\x00\xC0\x00\xC0\x15\xC0\x0F\xC8\x92\x71\xFC\x0D')
    ser.write(b'\xC0\x14\x05\x52\x07\x39\xC7\x0D\xE0\x50\xFA\x00\x00\x00\x00\x27\x02\x76\x04\x5D\x00\x71\x46\x0D')

    #packet7send(paramfile)
def strflt2bytes(inp, multiply = 1, bytesnum= 2):
    return int(float(inp[:-1])*multiply).to_bytes(bytesnum)

def packet1send(paramin):
    match paramin[0]:
        case "EM-30s\n":
            ctltype = b'\x05'
        case "EM-50s\n":
            ctltype = b'\x0A'
        case "EM-100s\n":
            ctltype = b'\x14'
        case "EM-150s\n":
            ctltype = b'\x1E'
        case "EM-200s\n":
            ctltype = b'\x28'
    match paramin[1]:
        case "48V\n":
            batv = b'\x00'
        case "60V\n":
            batv = b'\x01'
        case "72V\n":
            batv = b'\x02'
        case "84V\n":
            batv = b'\x03'
        case "96V\n":
            batv = b'\x04'
    buffer = sendheader + responemultibyte + votolRbyte + b'\x01' + ctltype + batv + strflt2bytes(paramin[2],10) + strflt2bytes(paramin[3],10) + strflt2bytes(paramin[4],10,1) + strflt2bytes(paramin[5]) + strflt2bytes(paramin[6]) + strflt2bytes(paramin[7],10) + strflt2bytes(paramin[8]) + strflt2bytes(paramin[9])
    ser.write(buffer+crc16(buffer)+b'\x0d')

def packet2send(paramin):
    select = 0
    buffer = sendheader + responemultibyte + votolRbyte + b'\x02' + strflt2bytes(paramin[10]) + strflt2bytes(paramin[11],1,1) + strflt2bytes(paramin[12],1,1) + strflt2bytes(paramin[13],1,1) + strflt2bytes(paramin[14]) + strflt2bytes(paramin[15]) + strflt2bytes(paramin[16])
    if paramin[17] == "ON\n": select += 1
    match paramin [18]:
        case "HIGH\n": select += 2
        case "MEDI\n": select += 4
        case "LOW\n": select += 8
    if paramin[19] == "VTYPE\n": select += 16
    if paramin[20] == "SWITCH\n": select += 32
    if paramin[21] == "ON\n": select += 64
    if paramin[22] == "ON\n": select += 128
    buffer = buffer + select.to_bytes(1) + strflt2bytes(paramin[23],1,1) + strflt2bytes(paramin[24],1,1) + strflt2bytes(paramin[25],1,1) + strflt2bytes(paramin[26],1,1) + strflt2bytes(paramin[27],1,1)
    ser.write(buffer+crc16(buffer)+b'\x0d')

def packet3send(paramin):
    select = 0
    if int(paramin[28]) < 0: hall = b'\xFF' + int((256-float(paramin[28])*-1)).to_bytes(1)
    if int(paramin[28]) > 0: hall = b'\x00' + int(paramin[28]).to_bytes(1)
    if paramin[36] == "ON\n": select += 8
    if paramin[37] == "YES\n": select += 16
    if paramin[38] == "YES\n": select += 32
    if paramin[39] == "ON\n": select += 64
    if paramin[40] == "REV\n": select += 128
    buffer = sendheader + responemultibyte + votolRbyte + b'\x03' + hall + strflt2bytes(paramin[29],1,1) + strflt2bytes(paramin[30],1,1) + strflt2bytes(paramin[31],1,1) + strflt2bytes(paramin[32]) + strflt2bytes(paramin[33]) + strflt2bytes(paramin[34]) + strflt2bytes(paramin[35],1,1) + select.to_bytes(1) + strflt2bytes(paramin[41],1,1) + strflt2bytes(paramin[42],1,1) + strflt2bytes(paramin[43],1,1) + strflt2bytes(paramin[44],1,1)
    ser.write(buffer+crc16(buffer)+b'\x0d')

def packet4send(paramin):
    select = 0
    if paramin[45] == "ON\n": select += 1
    if paramin[46] == "ON\n": select += 2
    if paramin[47] == "LIN\n": select += 4
    if paramin[48] == "ON\n": select += 8
    if paramin[49] == "ON\n": select += 16
    if paramin[50] == "HIGH\n": select += 32
    if paramin[51] == "ON\n": select += 64
    buffer = sendheader + responemultibyte +votolRbyte + b'\x04' + select.to_bytes(1) + strflt2bytes(paramin[52],327.67,2) + strflt2bytes(paramin[53],1,2) + strflt2bytes(paramin[54],1,2) + strflt2bytes(paramin[55],1,1) + strflt2bytes(paramin[56],1,1) +strflt2bytes(paramin[57],1,1) + strflt2bytes(paramin[58]) + strflt2bytes(paramin[59]) + strflt2bytes(paramin[60],1,2) + strflt2bytes(paramin[61],1,1)
    ser.write(buffer + crc16(buffer) + b'\x0d')

def packet7send(paramin):
    pass
def mainloop():
    exi = False
    count = 0
    msg = ''
    gear = ''
    state = ''
    global throttle
    while not exi:
        for c in ser.read():
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
                throttle = float("{:.2f}".format(int(d+format(c, '02x'),16)/5945))
                if throttle < 0.7:
                    throttle = 0.7
            if count == 16:
                signals=format(c, '02x')
                leftsig=signals[:1]
                rigtsig=signals[1:]
                switch = 'No'
                if leftsig == 'e' or leftsig == 'f':
                    state = 'BRL'
                    fustatus=b'\x37'
                    icstatus=b'\x05'
                    if leftsig == 'f':
                        switch = 'AxisV'
                if leftsig == 'c' or leftsig == 'd':
                    state = 'BR'
                    fustatus=b'\x17'
                    icstatus=b'\x05'
                    if leftsig == 'd':
                        switch = 'AxisV'
                if leftsig == 'a' or leftsig == 'b':
                    state = 'BL'
                    icstatus=b'\x05'
                    fustatus=b'\x30'
                    if leftsig == 'b':
                        switch = 'AxisV'
                if leftsig == '6' or leftsig == '7':
                    state = 'RL'
                    icstatus=b'\x05'
                    fustatus=b'\x27'
                    if leftsig == '7':
                        switch = 'AxisV'
                if leftsig == '8' or leftsig == '9':
                    state = 'B'
                    fustatus=b'\x10'
                    if leftsig == '9':
                        switch = 'AxisV'
                if leftsig == '4' or leftsig == '5':
                    state = 'R'
                    fustatus=b'\x07'
                    if leftsig == '5':
                        switch = 'AxisV'
                if leftsig == '2' or leftsig == '3':
                    state = 'L'
                    fustatus=b'\x20'
                    if leftsig == '3':
                        switch = 'AxisV'
                if leftsig == '0' or leftsig == '1':
                    state = 'None'
                    icstatus=b'\x03'
                    fustatus=b'\x00'
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
                    transmitDisp()
                count = 0
                msg = ''
if __name__ == "__main__":
    print("Votol Controller Emulator")
    mainloop()