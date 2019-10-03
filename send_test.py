import paho.mqtt.client as mqtt #import the client1

topic="8/motorised/north/0/0/traffic_light/0"
broker_address="91.121.165.36"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
print("connecting to broker")
client.connect(broker_address) #connect to broker
print("Publishing message to topic",topic)
client.publish(topic,0)
