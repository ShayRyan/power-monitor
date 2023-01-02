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

# open port - necessary?
if ser.isOpen() == False:
    ser.open()
ser.flushInput()
ser.flushOutput()

echostring = 'The quick brown fox jumped over the lazy dog.'

def echotest():
    while 1:
        ser.flushInput()
        ser.flushOutput()
        ser.write(echostring.encode())
        print(f'TX: {echostring}')
        time.sleep(0.5)
        rx = ser.readline().decode('utf-8')
        print(f'RX: {rx}')

def teardown():
    ser.close()
    print('Test complete')

if __name__ == '__main__':
    try:
        echotest()
    except KeyboardInterrupt:
        teardown()
    finally:
        teardown()

