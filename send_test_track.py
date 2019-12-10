import paho.mqtt.client as mqtt #import the client1
from random import randrange
from threading import Timer

group_no = 8#input("Group no: ")

class Message:
  def __init__(self, topic, payload):
    self.topic = topic
    self.payload = payload

messages =[Message(f"{group_no}/track/0/warning_light/0", 1),
           Message(f"{group_no}/track/0/barrier/0", 1)]

#broker = "test.mosquitto.org"
broker = "62.210.180.72"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
print("connecting to broker")
client.connect(broker) #connect to broker
for message in messages:
        print("Publishing message to topic", message.topic)
        client.publish(message.topic, message.payload)


