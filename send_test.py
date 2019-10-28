import paho.mqtt.client as mqtt #import the client1

group_no = input("Group no: ")

topic=f"{group_no}/foot/0/sensor/0/"
#broker = "test.mosquitto.org"
broker = "62.210.180.72"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
print("connecting to broker")
client.connect(broker) #connect to broker
print("Publishing message to topic",topic)
client.publish(topic,'1')
