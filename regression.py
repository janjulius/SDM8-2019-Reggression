import paho.mqtt.client as mqtt
import sys
from datetime import datetime

try: color = sys.stdout.shell
except AttributeError: raise RuntimeError("Use IDLE")

group_no = 8#input("Group no: ")

class Part:
    def __init__(self, value, next):
        self.value = value
        self.next = next

class Number_Part:
    def __init__(self, max, next, subs):
        self.max = max
        self.next = next
        self.subs = subs

class Sub_Part:
    def __init__(self, max, next):
        self.max = max
        self.next = next

class Payload_Part:
    def __init__(self, max):
        self.max = max

class Sub:
    def __init__(self, parent, max):
        self.parent = parent
        self.max = max

def is_sub(val):
    return type(val) == Sub

def is_number_part(val):
    return type(val) == Number_Part

def is_sub_part(val):
    return type(val) == Sub_Part

def is_part(val):
    return type(val) == Part

def is_multi_part(val):
    return type(val) == list and len(list(val)) >= 0 and type(val[0]) == Part

def is_payload_part(val):
    return type(val) == Payload_Part

def is_valid_part(split_topic, part):
    return part.value == split_topic

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

def check_valid_part(split_topic, current_part):
    #  STRING (component_type, lane_type) #
    if is_multi_part(current_part):
        for current_multi_part in current_part:
            if is_valid_part(split_topic, current_multi_part):
                # Valid string part
                return current_multi_part.next, True
        color.write(f"ERROR: invalid string, {split_topic}\n", "COMMENT")
        return None, False

    # INTEGER (group_id, component_id) # 
    elif is_number_part(current_part):
        split_topic, success = intTryParse(split_topic)
        if success:
            if int(split_topic) <= current_part.max:
                if current_part.subs == None:
                    # No subs for group
                    return current_part.next, True
                else:
                    for sub in current_part.subs:
                        if sub.parent == int(split_topic):
                            # Return valid subs for group (or NULL)
                            return Sub_Part(sub.max, current_part.next), True

                    # No subs for group so it should be NULL
                    return Sub_Part(None, current_part.next), True
            else:
                color.write(f"ERROR: invalid group, {split_topic}\n", "COMMENT")
                return None, False
        else:
           color.write(f"ERROR: not a number, {split_topic}\n", "COMMENT")
           return None, False

    # -- PAYLOAD --
    elif is_payload_part(current_part):
        split_topic, success = intTryParse(split_topic)
        if success:
            if int(split_topic) <= current_part.max:
                # Done, valid payload
                return None, True
            else:
                color.write(f"ERROR: invalid payload, {split_topic}\n", "COMMENT")
                return None, False
        else:
           color.write(f"ERROR: payload not a number, {split_topic}\n", "COMMENT")
           return None, False
        
    # -- SUB GROUP --
    elif is_sub_part(current_part):
        split_topic, success = intTryParse(split_topic)
        if success:
            if current_part.max is not None and int(split_topic) <= current_part.max:
                # Valid sup group, check next part
                return current_part.next, True
            else:
                color.write(f"ERROR: group does not have {split_topic} as subgroup\n", "COMMENT")
                return None, False  
        elif split_topic == 'NULL':
            # Subgroup can be NULL
            return current_part.next, True
        else:
            color.write(f"ERROR: invalid value in sub group, {split_topic}\n", "COMMENT")
            return None, False

    # -- STRING (component_type, lane_type) --
    elif is_part(current_part):
        if is_valid_part(split_topic, current_part):
            # Valid string part
            return current_part.next, True
        else:
            color.write(f"ERROR: invalid string, {split_topic}\n", "COMMENT")
            return None, False



def get_component(name, max_id, max_payload):
    return Part(name, Number_Part(max_id, Payload_Part(max_payload), None))
            
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

cycle_number_part = Number_Part(5, [traffic_light, sensor], [Sub(3, 1)])
cycle_part = Part("cycle", cycle_number_part)

vessel_number_part = Number_Part(1, [traffic_light, sensor, warning_light, barrier_vessel], [Sub(0, None)])
vessel_part = Part("vessel", vessel_number_part)

track_number_part = Number_Part(1, [traffic_light, sensor, warning_light, barrier_track], [Sub(0, None)])
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
    payload = msg.payload.decode('utf-8')
    color.write("\n#############################################\n\n", "KEYWORD")
    print(f"{datetime.now()}\nTOPIC: {msg.topic} - PAYLOAD: {payload}")

    split_topics = msg.topic.split('/', -1)
    split_topics = list(filter(None, split_topics))
    
    del split_topics[0] # Group no
    split_topics_length = len(split_topics)
        
    if split_topics_length == 5:
        split_topics.append(payload)
        current_part = valid_parts
        success = False
        
        for split_topic in split_topics:
            current_part, success = check_valid_part(split_topic, current_part)
            
            if not success:
                break

        if success:
            color.write("OK: valid topic\n", "STRING")
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
