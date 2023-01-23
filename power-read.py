#!/usr/bin/env python
from influxdb import InfluxDBClient
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

client = InfluxDBClient(host='localhost',
                        port=8086,
                        username='energyuser',
                        password='MirrorBeef#69')

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

def main():

    last_ts = 0

    try:
        while True:
            # read CC128 from UART
            line = ser.readline()

            # Time of reading
            now = datetime.now()
            this_ts = datetime.timestamp(now)
            local_time = now.strftime("%Y-%m-%d %H:%M:%S")

            # process line
            line = line.strip(b'\r\n')
            line = line.decode('utf-8')

            # ignore blank lines
            if line:
                decode_xml(line)
                xml_dict = decode_xml(line)

                # ignore energy history from cc128.
                # power readings marked by 'watts' in xml keys
                if 'watts' in xml_dict:
                    sensor_time = xml_dict['time'][0]
                    watts = int(xml_dict['watts'][0])

                    # need time interval to calculate energy. Do not store 1st reading.
                    if last_ts != 0:
                        energy = calc_energy(watts, (this_ts - last_ts))
                        interval = int(this_ts - last_ts)
                        this_ts_us = int(this_ts * 1_000_000)

                        line = f'power,sensor=cc128 watts={watts}i,sensor_utc="{sensor_time}",interval={interval}i,kwh={energy}'
                        #print(line)
                        client.write([line], {'db': 'house_power'}, 204, protocol=u'line')

                    last_ts = this_ts
            # loop for next reading

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, closing log file and exiting...")
    finally:
        client.close()

if __name__ == "__main__":
    main()


