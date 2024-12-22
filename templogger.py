import adafruit_dht
from ISStreamer.Streamer import Streamer
import board

import time
import requests
from datetime import datetime, timedelta
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# --------- Sensor Settings ---------
MINUTES_BETWEEN_READS = 2
METRIC_UNITS = True
# -----------------------------------

# --------- Server Settings ---------
file = open("settings.txt")
settings = file.readlines()
file.close()

# --------- Local settings ---------
SENSOR_LOCATION_NAME = settings[0].strip()
BUCKET_NAME = settings[1].strip()
BUCKET_KEY = settings[2].strip()
ACCESS_KEY = settings[3].strip()
URL = settings[4].strip()
URL_ALARM = settings[5].strip()
TEMP_ALARM = settings[6].strip()
HUMIDITY_ALARM = settings[7].strip()
# -----------------------------------


# -------- Report IP Address --------
IP = get_ip()
alarm_message = f"{SENSOR_LOCATION_NAME}: {IP}"
requests.post(URL,
              data = alarm_message.encode(encoding='utf-8'),
              headers = {"Title": "IP Update"})

# Connect sensor
dhtSensor = adafruit_dht.DHT22(board.D4)

# Output
streamer = Streamer(bucket_name = BUCKET_NAME,
                    bucket_key = BUCKET_KEY,
                    access_key = ACCESS_KEY)

# Set these to current time at the start so that alarms will
# trigger after the desired time.
last_temp_alarm = datetime.now()
last_humidity_alarm = datetime.now()
last_ip_check = datetime.now()

while True:
    try:
        humidity = dhtSensor.humidity
        temp_c = dhtSensor.temperature
    except RuntimeError:
        continue

    try:
        if METRIC_UNITS:
            streamer.log(SENSOR_LOCATION_NAME + " Temperature (C)", temp_c)
        else:
            temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
            streamer.log(SENSOR_LOCATION_NAME + " Temperature (F)", temp_f)
        humidity = format(humidity,".2f")
        streamer.log(SENSOR_LOCATION_NAME + " Humidity (%)", humidity)
        streamer.flush()
    except TypeError:
        continue

    # Temperature alarm
    if float(temp_c) >= TEMP_ALARM:
        if  (datetime.now() - last_temp_alarm) > timedelta(minutes=5):
            alarm_message = f"Temperature in {SENSOR_LOCATION_NAME} is {temp_c:.1f}"

            requests.post(URL_ALARM,
                          data=alarm_message.encode(encoding='utf-8'),
                          headers={"Title": "Temperature Alarm",
                                   "Priority": "urgent",
                                   "Tags": "warning"})

            last_temp_alarm = datetime.now()

    # Humidity alarm
    if float(humidity) <= HUMIDITY_ALARM:
        if  (datetime.now() - last_humidity_alarm) > timedelta(minutes=5):
            alarm_message = f"Humidity in {SENSOR_LOCATION_NAME} is {humidity:.1f}"

            requests.post(URL_ALARM,
                          data=alarm_message.encode(encoding='utf-8'),
                          headers={"Title": "Humidity Alarm",
                                   "Priority": "urgent",
                                   "Tags": "warning"})

            last_humidity_alarm = datetime.now()

    # IP check
    if  (datetime.now() - last_ip_check) > timedelta(hours=24):
        IP_new = get_ip()
        if IP_new != IP:
            IP = IP_new
            alarm_message = f"{SENSOR_LOCATION_NAME}: {IP}"
            requests.post(URL,
                          data = alarm_message.encode(encoding='utf-8'),
                          headers = {"Title": "IP Update"})

        last_ip_check = datetime.now()

    time.sleep(60 * MINUTES_BETWEEN_READS)
