import paho.mqtt.client as mqtt
import os, sys

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "functions"))

from TopicValidator import TopicValidator
from cust_logging import print_seperator

group_no = 8#input("Group no: ")

topic_validator = TopicValidator()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    topic=f'{group_no}/#'
    client.subscribe(topic)
    print(f'Connected to {topic} with group {group_no}')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    
    print_seperator()
    print(f'TOPIC: {msg.topic} - PAYLOAD: {payload}')

    topic_validator.validate(msg.topic, payload)
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

broker = "62.210.180.72"
client.connect(broker, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
