import paho.mqtt.client as mqtt

group_no = input("Group no: ")

class Part:
    def __init__(self, value, next):
        self.value = value
        self.next = next

class Number_Part:
    def __init__(self, max, next, subs):
        self.max = max
        self.next = next
        self.subs = subs

class Sub:
    def __init__(self, parent, max):
        self.parent = parent
        self.max = max

def is_sub(val):
    return type(val) == Sub

def is_number_part(val):
    return type(val) == Number_Part

def is_part(val):
    return type(val) == Part

def is_multi_part(val):
    return type(val) == list and len(list(val)) >= 0 and type(val[0]) == Part

def is_valid_part(split_topic, part):
    return part.value == split_topic

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

def check_valid_part(split_topic, current_part, has_sub):
          
    if is_multi_part(current_part):
        for current_multi_part in current_part:
            if is_valid_part(split_topic, current_multi_part):
                return current_multi_part.next, True
        print("ERROR: invalid part, " + current_part)
        return None, False
                    
    elif is_number_part(current_part):
        split_topic, success = intTryParse(split_topic)
        if success:
            if int(split_topic) <= current_part.max:
                if has_sub:
                    if current_part.subs == None:
                        return current_part.next, True
                    else:
                        for sub in current_part.subs:
                            if sub.parent == int(split_topic):
                                return Number_Part(sub.max, current_part.next, None), True
                        print("ERROR: invalid number, " + current_part)
                        return None, False
                else:
                    return current_part.next, True
            else:
                print("ERROR: invalid number, " + current_part)
                return None, False
        else:
           print("ERROR: invalid int in number, " + current_part)
           return None, False
                
    elif is_part(current_part):
        if is_valid_part(split_topic, current_part):
            return current_part.next, True
        else:
            print("ERROR: invalid part, " + current_part)
            return None, False

def get_component(name, max_id, max_payload):
    return Part(name, Number_Part(max_id, Number_Part(max_payload, None, None), None))
            
sensor_motorised = get_component("sensor", 1, 1)
sensor = get_component("sensor", 0, 1)

traffic_light = get_component("traffic_light", 0, 3)
warning_light = get_component("warning_light", 0, 1)

barrier_vessel = get_component("barrier", 7, 1)
barrier_track = get_component("barrier", 8, 1)

motorised_number_part = Number_Part(8, [traffic_light, sensor_motorised], [Sub(1, 1), Sub(5, 1)])
motorised_part = Part("motorised", motorised_number_part)

foot_number_part = Number_Part(7, [traffic_light, sensor], [Sub(0, 1), Sub(1, 1), Sub(4, 2), Sub(5, 2)])
foot_part = Part("foot", foot_number_part)

cycle_number_part = Number_Part(5, [traffic_light, sensor_motorised], [Sub(3, 1)])
cycle_part = Part("cycle", cycle_number_part)

vessel_number_part = Number_Part(1, [traffic_light, sensor_motorised, warning_light, barrier_vessel], None)
vessel_part = Part("vessel", vessel_number_part)

track_number_part = Number_Part(1, [traffic_light, sensor_motorised, warning_light, barrier_track], None)
track_part = Part("track", track_number_part)

valid_parts = [motorised_part, foot_part, cycle_part, vessel_part, track_part]

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
    print(msg.topic+" "+str(msg.payload))

    split_topics = msg.topic.split('/', -1)
    split_topics = list(filter(None, split_topics))
    
    del split_topics[0]
    split_topics_length = len(split_topics)
    
    has_sub = split_topics_length == 5

    has_vessel_or_track = "vessel" in msg.topic or "track" in msg.topic
    
    if split_topics_length == 4 or (split_topics_length == 5 and not has_vessel_or_track):
        split_topics.append(msg.payload.decode('utf-8'))
        current_part = valid_parts
        success = False
        
        for split_topic in split_topics:
            current_part, success = check_valid_part(split_topic, current_part, has_sub)
            if not success:
                break

        if success:
            print("OK: valid topic")
    else:
        print('ERROR: invalid topic length')
    

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
