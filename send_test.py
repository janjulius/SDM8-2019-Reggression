import paho.mqtt.client as mqtt #import the client1
from random import randrange

group_no = 8#input("Group no: ")

topics=[f"{group_no}/foot/0/NULL/sensor/0/",
f"{group_no}/foot/0/1/sensor/0/",
f"{group_no}/foot/0/1/sensor/0/",
f"{group_no}/vessel/0/NULL/sensor/0/",
f"{group_no}/vessel/0/1/sensor/0/",
f"{group_no}/motorised/0/1/sensor/0/",
f"{group_no}/motorised/0/NULL/traffiac_light/0/",
f"{group_no}/vessel/0/1/sensor/0/",
f"{group_no}/vessel/0/1/sensor/0/",
f"{group_no}/foot/3/NULL/sensor/0/",
f"{group_no}/foot/2/1/traffic_light/0/",
f"{group_no}/fogot/4/NULL/traffic_light/0/"]

#broker = "test.mosquitto.org"
broker = "62.210.180.72"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
print("connecting to broker")
client.connect(broker) #connect to broker
for topic in topics:
	print("Publishing message to topic",topic)
	client.publish(topic,randrange(3))
