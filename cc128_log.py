#!/usr/bin/env python
import time
import serial

ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate = 57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=3
)

with open('cc128.log', mode='a') as f:
    while 1:
        line = ser.readline()
        line = line.decode('utf-8')
        print(line)
        f.write(line)
        f.flush()

