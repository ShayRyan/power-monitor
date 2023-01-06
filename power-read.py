#!/usr/bin/env python
import time
import serial
import xml.etree.ElementTree as et

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=3
)

def parse_xml(xml_string):
    # Parse the XML string
    root = et.fromstring(xml_string)

    # Access the elements and attributes of the XML tree
    for element in root:
        print(f'Element: {element.tag} -> {element.text}')
        for child in element:
            print(f'Child: {child.tag} -> {child.text}')
while 1:
    line = ser.readline()
    line = line.strip(b'\r\n')
    line = line.decode('utf-8')
    if line:
        parse_xml(line)
