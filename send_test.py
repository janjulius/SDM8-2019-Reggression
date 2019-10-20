import paho.mqtt.client as mqtt #import the client1

topic="8/foot/0/sensor/0/"
broker = "test.mosquitto.org"
#broker = "91.121.165.36"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
print("connecting to broker")
client.connect(broker) #connect to broker
print("Publishing message to topic",topic)
client.publish(topic,'1')
