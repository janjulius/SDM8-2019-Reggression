import paho.mqtt.client as mqtt

group_no = 8#input("Geef groep nr: ")

class Part:
    def __init__(self, name, next):
        self.name = name
        self.next = next

class Id_Part:
    def __init__(self, max, next):
        self.max = max
        self.next = next
        self.subs = subs

class Sub:
    def __init__(self, parent, max, next):
        self.parent = parent
        self.max = max


def is_sub(val):
    return type(val) == Sub

def is_id_part(val):
    return type(val) == Id_Part

def is_part(val):
    return type(val) == Part

def is_multi_part(val):
    return type(val) == list and len(list(val)) >= 0 and type(val[0]) == Part

def is_valid_part(split_topic, part):
    return part.name == split_topic

def check_valid_part(split_topic, current_part, has_sub):
        if is_multi_part(current_part):
            for current_multi_part in current_part:
                if is_valid_part(split_topic, current_multi_part)
                    print("valid part")
                    return current_multi_part.next
            print("invalid part")
            return None
                    
        elif is_id_part(current_part):
            if int(split_topic) <= current_part.max:
                if has_sub:
                    # check for subs
                    if current_part.subs == None:
                        print("no subs for part, continue")
                    else:
                        # TODO get sub.. return new part with sub max.
                        return None
                else
                    print("no subs in topic, continue")
                    return current_part.next
                
        elif is_part(current_part):
            if is_valid_part(split_topic, current_part):
                print("valid part")
                return current_part.next
            else:
                print("invalid part")
                return None
                
            
    
motorised_traffic_light = Part("traffic_light", Id_Part(0, None, None))
motorised_sensor = Part("sensor", Id_Part(1, None, None))
motorised_id_part = Id_Part(8, [motorised_traffic_light, motorised_sensor], [Sub(1, 1), Sub(5, 1)])
motorised_part = Part("motorised", motorised_id_part)

valid_parts = [motorised_part]

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
    split_topics = list(filter(None, split_topics))
    del split_topics[0]
    split_topics_length = len(split_topics)
    has_sub = split_topics_length == 5
    
    if split_topics_length == 4 or split_topics_length == 5:
        print(f'valid topic length {split_topics_length}')
        current_part = valid_parts
        
        for split_topic in split_topics:
            print(split_topic)
            current_part = check_valid_part(split_topic, current_part, has_sub)       
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
