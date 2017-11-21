#server_host = "avvmtemplate.dev.unitedplanet.de"
server_host = "thomasf.unitedplanet.de"
server_port = 8883
cert_path = "/opt/activemq/conf/my_broker_cert.pem"
privkey_path = "/opt/activemq/conf/my_client_key.pem"
privcert_path = "/opt/activemq/conf/my_client_cert.pem"

subs_username = "user_cons"
subs_password = "admin"
subs_topic = "test-mqtt/cputemp2"
subs_clientid = "TomSubsClient"

publ_username = "user_publ"
publ_password = "admin"
publ_topic = subs_topic
publ_clientid = "TomPublClient"
publ_qos = 1

last_will_queue = "tom/alarm"
