from VesselValidator import VesselValidator
from TrackValidator import TrackValidator
from cust_logging import log_error, log_message, log_warning

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

class TopicValidator:
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
	track_light_max_payload = 1

	vessel_group_max_id = 0
	vessel_light_max_id = 1
	vessel_sensor_max_id = 3
	vessel_light_max_payload = 1

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
	train_light = Component("train_light", track_light_max_id, track_light_max_payload)
	boat_light = Component("boat_light", vessel_light_max_id, vessel_light_max_payload)

	motorised = Topic("motorised", motorised_group_max_id, [traffic_light, motorised_sensor])
	foot = Topic("foot", foot_group_max_id, [traffic_light, foot_sensor])
	cycle = Topic("cycle", cycle_group_max_id, [traffic_light, cycle_sensor])
	vessel = Topic("vessel", vessel_group_max_id, [vessel_sensor, warning_light, barrier, boat_light, deck])
	track = Topic("track", track_group_max_id, [track_sensor, warning_light, barrier, train_light])

	valid_parts = [motorised, foot, cycle, vessel, track]
	
	vessel_validator = VesselValidator()
	track_validator = TrackValidator()
	
	def validate(self, topic, payload):
		split_topics = topic.split('/', -1)

		del split_topics[0] # Team id
			
		if len(split_topics) == 4:
			lane_type = split_topics[0]
			group_id = split_topics[1]
			component_type = split_topics[2]
			component_id = split_topics[3]
			
			group_id, is_int = self.intTryParse(group_id)
			if not is_int:
				log_error(f'invalid int group_id {group_id}')
				return
			
			component_id, is_int = self.intTryParse(component_id)
			if not is_int:
				log_error(f'invalid int component_id {component_id}')
				return
			
			payload, is_int = self.intTryParse(payload)
			if not is_int:
				log_error(f'invalid int payload {payload}')
				return

			self.track_validator.validate(topic, payload)
			self.vessel_validator.validate(topic, payload)

			found_lane_type = False
			found_component_type = False

			# Check lane_type
			for valid_part in self.valid_parts:
				if valid_part.lane_type == lane_type: 
					found_lane_type = True
					
					# Check group_id
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
										log_message("valid topic")
									else:
										log_error(f'invalid payload {payload}\nMAX: {component.max_payload}')
								else:
									# invalid component id
									log_error(f'invalid component_id {component_id}\nMAX: {component.max_component_id}')
									
						# not found error
						if not found_component_type:
							valid_component_types = []
							for component in valid_part.components:
								valid_component_types.append(component.value)
							valid_components_string = ", ".join(valid_component_types)
							
							log_error(f'invalid component_type {component_type}\nALLOWED: {valid_components_string}')
					else:
						# invalid group_id
						log_error(f'invalid group_id {group_id}\nMAX: {valid_part.max_group_id}')
						
			# not found error
			if not found_lane_type:
				valid_lanes = []
				for valid_part in valid_parts:
					valid_lanes.append(valid_part.lane_type)
				valid_lanes_string = ", ".join(valid_lanes)
				
				log_error(f'invalid lane_type {lane_type}\nALLOWED: {valid_lanes_string}')
			
		else:
			log_error(f'invalid topic length {len(split_topics)}')   
	
	def intTryParse(self, value):
		try:
			return int(value), True
		except ValueError:
			return value, False 