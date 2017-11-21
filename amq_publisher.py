#!/usr/bin/env python3


import time
import paho.mqtt.client as mqtt
from static import *
import ssl

tls = {
  'keyfile':privkey_path
}

def get_cputemp():
    with open('/sys/class/thermal/thermal_zone2/temp',"r", encoding="utf-8") as f:
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
#client.tls_set(cert_path)
client.tls_set(ca_certs=cert_path,certfile=privcert_path, keyfile=privkey_path)
#client.tls_set(certfile=cert_path)
#client.tls_set(privkey_path)
#client.tls_set(ca_certs=cert_path, keyfile=privkey_path)

client.connect(server_host, server_port, 60)
client.loop_start()

while True:
    my_message = str(get_cputemp())
    # qos=2, retain=True
    client.publish(subs_topic, my_message, publ_qos)
    print("Sent: \"%s\"" % (my_message))
    time.sleep(2)
