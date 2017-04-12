server_host = "avvmtemplate.dev.unitedplanet.de"
server_port = 8883
cert_path = "broker.pem"

subs_username = "user_cons"
subs_password = "admin"
subs_topic = "test-mqtt/fanspeed"
subs_clientid = "TomSubsClient"

publ_username = "user_publ"
publ_password = "admin"
publ_topic = subs_topic
publ_clientid = "TomPublClient"
publ_qos = 1

last_will_queue = "tom/alarm"
