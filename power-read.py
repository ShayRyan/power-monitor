#!/usr/bin/env python
from datetime import datetime
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

def decode_xml(xml_string):
    """Decode an XML string to the full extent from root to leaves."""

    xml_tree = et.fromstring(xml_string)
    xml_dict = {}

    def parse_element(element):
        for child in element:
            if len(child) > 0:
                parse_element(child)
            if child.tag in xml_dict:
                xml_dict[child.tag].append(child.text)
            else:
                xml_dict[child.tag] = [child.text]

    parse_element(xml_tree)

    return xml_dict

def calc_energy(pwr, sec):
    """Power in watts, time in seconds. Return energy in kWhr"""

    joules = pwr * sec
    watt_hours = joules / 3600
    kilo_watt_hours = watt_hours / 1000

    return kilo_watt_hours

last_ts = 0
while True:
    # Time of reading
    now = datetime.now()
    this_ts = datetime.timestamp(now)
    local_time = now.strftime("%Y-%m-%d %H:%M:%S")

    line = ser.readline()
    line = line.strip(b'\r\n')
    line = line.decode('utf-8')
    if line:
        decode_xml(line)
        xml_dict = decode_xml(line)
        #print(xml_dict)

        if 'watts' in xml_dict:
            sensor_time = xml_dict['time'][0]
            power = int(xml_dict['watts'][0])
            tempr = float(xml_dict['tmpr'][0])

            if last_ts == 0:
                energy = 0
            else:
                energy = calc_energy(power, (this_ts - last_ts))

            print(f"{local_time} -> Sensor Time= {sensor_time} "
                  f"Temp= {tempr} C Power= {power} W Energy= {energy} kWh")

            last_ts = this_ts

# add main

# add timestamp for time of receipt
# print tor and message
# write to CSV
# write to SQLite DB
