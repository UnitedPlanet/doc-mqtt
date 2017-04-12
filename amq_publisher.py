#!/usr/bin/env python3

import time
import paho.mqtt.client as mqtt
from static import *

def get_fanspeed():
    with open('/sys/devices/platform/it87.656/fan1_input',"r", encoding="utf-8") as f:
        return f.readline().strip('\n')

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect

# last will
client.will_set(last_will_queue, "ALARM", 0, False)

# authentication
client.username_pw_set(publ_username, publ_password)

# TLS set path to broker certificate
client.tls_set(cert_path)

client.connect(server_host, server_port, 60)
client.loop_start()

while True:
    my_message = str(get_fanspeed())
    # qos=2, retain=True
    client.publish(subs_topic, my_message, publ_qos)
    print("Sent: \"%s\"" % (my_message))
    time.sleep(2)
