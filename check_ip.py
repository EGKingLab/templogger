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
