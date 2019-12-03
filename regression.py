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

class Topic:
    def __init__(self, lane_type, max_group_id, components):
        self.lane_type = lane_type
        self.max_group_id = max_group_id
        self.components = components

class Odd_Rules:
    def __init__(self, group_id, max):
        self.group_id = group_id
        self.max = max

class Component:
    def __init__(self, value, max_component_id, max_payload, odd_rules = None):
        self.value = value
        self.max_component_id = max_component_id
        self.max_payload = max_payload
        self.odd_rules = odd_rules

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False       

odd_motorised_sensor = [Odd_Rules(1, motorised_sensor_dual_lane_max_id), Odd_Rules(5, motorised_sensor_dual_lane_max_id)]
odd_cycle_sensor = [Odd_Rules(3, cycle_sensor_two_way_max_id), Odd_Rules(4, cycle_sensor_two_way_max_id)]
           
track_sensor = Component("sensor", track_sensor_max_id, sensor_max_payload)
vessel_sensor = Component("sensor", vessel_sensor_max_id, sensor_max_payload)
foot_sensor = Component("sensor", foot_sensor_max_id, sensor_max_payload)
cycle_sensor = Component("sensor", cycle_sensor_one_way_max_id, sensor_max_payload, odd_cycle_sensor)
motorised_sensor = Component("sensor", motorised_sensor_single_lane_max_id, sensor_max_payload, odd_motorised_sensor)

deck = Component("deck", deck_max_id, deck_max_payload)
barrier = Component("barrier", barrier_max_id, barrier_max_payload)

traffic_light = Component("traffic_light", traffic_light_max_id, traffic_light_max_payload)
warning_light = Component("warning_light", warning_light_max_id, warning_light_max_payload)
train_light = Component("train_light", warning_light_max_id, warning_light_max_payload)

motorised = Topic("motorised", motorised_group_max_id, [traffic_light, motorised_sensor])
foot = Topic("foot", foot_group_max_id, [traffic_light, foot_sensor])
cycle = Topic("cycle", cycle_group_max_id, [traffic_light, cycle_sensor])
vessel = Topic("vessel", vessel_group_max_id, [traffic_light, vessel_sensor, warning_light, barrier])
track = Topic("track", track_group_max_id, [traffic_light, track_sensor, warning_light, barrier])

valid_parts = [motorised, foot, cycle, vessel, track]

def check_valid_topic(topic, payload):
    split_topics = topic.split('/', -1)
    split_topics = list(filter(None, split_topics))
    
    del split_topics[0] # Group no    
        
    if len(split_topics) == 4:
        lane_type = split_topics[0]
        group_id = split_topics[1]
        component_type = split_topics[2]
        component_id = split_topics[3]

        group_id, is_int = intTryParse(group_id)
        if not is_int:
            color.write(f'ERROR: invalid int group_id {group_id}', "COMMENT");
            return

        component_id, is_int = intTryParse(component_id)
        if not is_int:
            color.write(f'ERROR: invalid int component_id {component_id}', "COMMENT");
            return
        
        payload, is_int = intTryParse(payload)
        if not is_int:
            color.write(f'ERROR: invalid int payload {payload}', "COMMENT");
            return       

        found_lane_type = False
        found_component_type = False

        # Check lane_type
        for valid_part in valid_parts:
            if valid_part.lane_type == lane_type: 
                found_lane_type = True

                # Check group_id
                group_id, is_int = intTryParse(group_id)                
                if int(group_id) <= valid_part.max_group_id:

                    # Check component_type
                    for component in valid_part.components:
                        if component.value == component_type:
                            found_component_type = True

                            # Check for odd rules
                            if component.odd_rules is not None:
                                for odd_rule in component.odd_rules:
                                    if odd_rule.group_id == int(group_id):
                                        component.max_component_id = odd_rule.max


                            # Check component_id
                            if int(component_id) <= component.max_component_id:
                                if int(payload) <= component.max_payload:
                                    color.write("OK: valid topic\n", "STRING")
                                else:
                                    color.write(f'ERROR: invalid payload {payload}\n', "COMMENT");
                            else:
                                # invalid component id
                                color.write(f'ERROR: invalid component_id {component_id}\n', "COMMENT");
                                
                    # not found error
                    if not found_component_type:
                        color.write(f'ERROR: invalid component_type {component_type}\n', "COMMENT");
                else:
                    # invalid group_id
                    color.write(f'ERROR: invalid group_id {group_id}\n', "COMMENT");
                    
        # not found error
        if not found_lane_type:
            color.write(f'ERROR: invalid lane_type {lane_type}\n', "COMMENT");
        
    else:
        color.write(f'ERROR: invalid topic length {split_topics_length}\n', "COMMENT");


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

    check_valid_topic(msg.topic, payload)
    

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
