#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from static import *

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(subs_topic)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client(subs_clientid, clean_session=False)

client.on_connect = on_connect
client.on_message = on_message

# authentication
client.username_pw_set(subs_username, subs_password)

# TLS set path to broker certificate
client.tls_set(cert_path)

client.connect(server_host, server_port, 60)

client.loop_forever()
