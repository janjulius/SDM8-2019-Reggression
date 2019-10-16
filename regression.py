import paho.mqtt.client as mqtt

group_no = 8#input("Geef groep nr: ")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    topic=f'{group_no}/#'
    client.subscribe(topic)
    print(f'Connected with group {group_no}')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    split_topics = msg.topic.split('/', -1)
    print("ey")
    split_topics = filter(None, split_topics)
    split_topics_length = len(split_topics)
    print(split_topics_length)
    
    if split_topics_length == 5:
        print('valid topic length')
        # ok
    elif split_topics_length == 6:
        print('valid topic length')
        # ok
    else:
        print('invalid topic length')
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("91.121.165.36", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
