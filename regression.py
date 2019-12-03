import paho.mqtt.client as mqtt
import sys
from datetime import datetime

try: color = sys.stdout.shell
except AttributeError: raise RuntimeError("Use IDLE")

group_no = 8#input("Group no: ")

sensor_max_payload = 1

traffic_light_max_id = 0
traffic_light_max_payload = 2

warning_light_max_id = 0
warning_light_max_payload = 1

barrier_max_id = 0
barrier_max_payload = 1

deck_max_id = 0
deck_max_payload = 1

motorised_group_max_id = 8
motorised_sensor_single_lane_max_id = 1
motorised_sensor_dual_lane_max_id = 3

cycle_group_max_id = 4
cycle_sensor_one_way_max_id = 0
cycle_sensor_two_way_max_id = 1

foot_group_max_id = 6
foot_sensor_max_id = 1

track_group_max_id = 0
track_sensor_max_id = 2
track_light_max_id = 1

vessel_group_max_id = 0
vessel_light_max_id = 1
vessel_sensor_max_id = 3
vessel_light_max_payload = 1

bridge_barriers_open = True
deck_open = False
deck_sensor_clear = True
under_deck_sensor_clear = True
vessel_warning_lights_on = False
boat_light_0_green = False
boat_light_1_green = False

track_barriers_open = True
crossing_clear = True
track_east_clear = True
track_west_clear = True
track_warning_lights_on = False


class Odd_Sensor:
    def __init__(self, group_id, max):
        self.group_id = group_id
        self.max = max

class Part:
    def __init__(self, value, next):
        self.value = value
        self.next = next

class Odd_Sensor_Part:
    def __init__(self, max, next, odd_parts):
        self.max = max
        self.next = next
        self.odd_parts = odd_parts

class Number_Part:
    def __init__(self, max, next):
        self.max = max
        self.next = next

class Payload_Part:
    def __init__(self, max):
        self.max = max

def is_number_part(val):
    return type(val) == Number_Part

def is_odd_sensor_part(val):
    return type(val) == Odd_Sensor_Part

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
    # STRING (component_type, lane_type) #
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
                # Done, valid number part
                return current_part.next, True
            else:
                color.write(f"ERROR: invalid group, {split_topic}\n", "COMMENT")
                return None, False
        else:
           color.write(f"ERROR: not a number, {split_topic}\n", "COMMENT")
           return None, False

    # ODD SENSOR PART (component_id) # 
    elif is_odd_sensor_part(current_part):
        print(current_part.max, split_topic)
        split_topic, success = intTryParse(split_topic)
        if success:
            for odd_part in current_part.odd_parts:
                print(odd_part.group_id, odd_part.max)
                if odd_part.group_id == int(split_topic):     
                    return current_part.next, True
            if int(split_topic) <= current_part.max:
                # Done, valid number part
                return current_part.next, True
            else:
                color.write(f"ERROR: invalid sensor, {split_topic}\n", "COMMENT")
                return None, False
        else:
           color.write(f"ERROR: not a number, {split_topic}\n", "COMMENT")
           return None, False


   # PAYLOAD #
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

    # STRING (component_type, lane_type) #
    elif is_part(current_part):
        if is_valid_part(split_topic, current_part):
            # Valid string part
            return current_part.next, True
        else:
            color.write(f"ERROR: invalid string, {split_topic}\n", "COMMENT")
            return None, False



def get_component(name, max_id, max_payload):
    return Part(name, Number_Part(max_id, Payload_Part(max_payload)))

def get_odd_sensor_component(name, max_id, max_payload, odd_parts):
    return Part(name, Odd_Sensor_Part(max_id, Payload_Part(max_payload), odd_parts))

odd_motorised_sensor = [Odd_Sensor(1, motorised_sensor_dual_lane_max_id), Odd_Sensor(5, motorised_sensor_dual_lane_max_id)]
odd_cycle_sensor = [Odd_Sensor(3, cycle_sensor_two_way_max_id), Odd_Sensor(4, cycle_sensor_two_way_max_id)]
           
track_sensor = get_component("sensor", track_sensor_max_id, sensor_max_payload)
vessel_sensor = get_component("sensor", vessel_sensor_max_id, sensor_max_payload)
foot_sensor = get_component("sensor", foot_sensor_max_id, sensor_max_payload)
cycle_sensor = get_odd_sensor_component("sensor", cycle_sensor_one_way_max_id, sensor_max_payload, odd_cycle_sensor)
motorised_sensor = get_odd_sensor_component("sensor", motorised_sensor_single_lane_max_id, sensor_max_payload, odd_motorised_sensor)

deck = get_component("deck", deck_max_id, deck_max_payload)
barrier = get_component("barrier", barrier_max_id, barrier_max_payload)

traffic_light = get_component("traffic_light", traffic_light_max_id, traffic_light_max_payload)
warning_light = get_component("warning_light", warning_light_max_id, warning_light_max_payload)
train_light = get_component("train_light", warning_light_max_id, warning_light_max_payload)

motorised_number_part = Number_Part(motorised_group_max_id, [traffic_light, motorised_sensor])
motorised_part = Part("motorised", motorised_number_part)

foot_number_part = Number_Part(foot_group_max_id, [traffic_light, foot_sensor])
foot_part = Part("foot", foot_number_part)

cycle_number_part = Number_Part(cycle_group_max_id, [traffic_light, cycle_sensor])
cycle_part = Part("cycle", cycle_number_part)

vessel_number_part = Number_Part(vessel_group_max_id, [traffic_light, vessel_sensor, warning_light, barrier])
vessel_part = Part("vessel", vessel_number_part)

track_number_part = Number_Part(track_group_max_id, [traffic_light, track_sensor, warning_light, barrier])
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
        
    if split_topics_length == 4:
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
        color.write(f'ERROR: invalid topic length {split_topics_length}', "COMMENT");
    

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
