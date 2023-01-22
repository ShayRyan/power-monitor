#!/usr/bin/env python
from datetime import datetime
import serial
import csv
import xml.etree.ElementTree as et

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=3
)

log_file_name = "log.csv"
header = ['timestamp', 'local_time', 'sensor_time', 'temp', 'power', 'energy']

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
        with open(log_file_name, mode='w', newline='') as log_file:
            log_writer = csv.writer(log_file)
            log_writer.writerow(header)

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

                    # ignore energy history, 'watts' in power reading only
                    if 'watts' in xml_dict:
                        sensor_time = xml_dict['time'][0]
                        power = int(xml_dict['watts'][0])
                        tempr = float(xml_dict['tmpr'][0])

                        # need time interval to calculate energy. Wait for 2nd reading.
                        if last_ts == 0:
                            energy = 0
                        else:
                            energy = calc_energy(power, (this_ts - last_ts))

                        # write observation to log
                        row = [this_ts, local_time, sensor_time, tempr, power, energy]
                        log_writer.writerow(row)

                        #print(f"{local_time} -> Sensor Time= {sensor_time} "
                        #      f"Temp= {tempr} C Power= {power} W Energy= {energy} kWh")

                        last_ts = this_ts
            # loop for next reading

    except KeyboardInterrupt:
        print("Keyboard interrupt detected, closing log file and exiting...")
    finally:
        log_file.close()

if __name__ == "__main__":
    main()


# add time of receipt time delta and sensor timestamp time delta
# write to CSV - daily file
# write to SQLite DB
