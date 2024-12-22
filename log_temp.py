import adafruit_dht
from ISStreamer.Streamer import Streamer
import board

import time
import requests
from datetime import datetime, timedelta
import socket

# --------- Sensor Settings ---------
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

# Connect sensor
dhtSensor = adafruit_dht.DHT22(board.D4)

# Output
streamer = Streamer(bucket_name = BUCKET_NAME,
                    bucket_key = BUCKET_KEY,
                    access_key = ACCESS_KEY)

while True:
    try:
        humidity = dhtSensor.humidity
        temp_c = dhtSensor.temperature
        break
    except RuntimeError:
        time.sleep(2)

if METRIC_UNITS:
    streamer.log(SENSOR_LOCATION_NAME + " Temperature (C)", str(temp_c))
else:
    temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
    streamer.log(SENSOR_LOCATION_NAME + " Temperature (F)", temp_f)

streamer.log(SENSOR_LOCATION_NAME + " Humidity (%)", str(humidity))
streamer.flush()

# Temperature alarm
if float(temp_c) >= float(TEMP_ALARM):
    alarm_message = f"Temperature in {SENSOR_LOCATION_NAME} is {temp_c:.1f}"

    requests.post(URL_ALARM,
                    data=alarm_message.encode(encoding='utf-8'),
                    headers={"Title": "Temperature Alarm",
                            "Priority": "urgent",
                            "Tags": "warning"})

# Humidity alarm
if float(humidity) <= float(HUMIDITY_ALARM):
    alarm_message = f"Humidity in {SENSOR_LOCATION_NAME} is {humidity:.1f}"

    requests.post(URL_ALARM,
                    data=alarm_message.encode(encoding='utf-8'),
                    headers={"Title": "Humidity Alarm",
                            "Priority": "urgent",
                            "Tags": "warning"})
