#!/usr/bin/env python3

import time
import paho.mqtt.client as mqtt
from static import *

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

count = 0

while True:
    time.sleep(2)
    count += 1
    my_message = "Tom's message no. " + str(count)
    #client.publish("tom/topics/mytopic1", my_message, qos=2, retain=True)
    client.publish(subs_topic, my_message, qos=1)
    print(my_message + " sent...")
