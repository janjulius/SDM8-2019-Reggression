from check_statement import check_statement
from cust_logging import log_warning
from threading import Thread, Timer

class VesselValidator:
	bridge_barriers_open = True
	deck_open = False
	deck_sensor_clear = True
	under_deck_sensor_clear = True
	vessel_warning_lights_on = False
	boat_light_0_green = False
	boat_light_1_green = False

	def validate(topic, payload):
		global bridge_barriers_open
		global deck_open
		global deck_sensor_clear
		global under_deck_sensor_clear
		global vessel_warning_lights_on
		global boat_light_0_green
		global boat_light_1_green

		if "/vessel/0/boat_light/0" in topic:
			if payload == 1 and not deck_open:
				log_warning("deck is closed can not turn lights green")
			boat_light_0_green = payload == 1
		elif "/vessel/0/boat_light/1" in topic:
			if payload == 1 and not deck_open:
				log_warning("deck is closed can not turn lights green")
			boat_light_1_green = payload == 1;
		elif "/vessel/0/warning_light/0" in topic:
			if payload == 0:
				if deck_open:
					log_warning("not allowed to turn off warning_light when deck is open");
				if not bridge_barriers_open:
					log_warning("not allowed to turn off warning_light, barriers are still closed");
			vessel_warning_lights_on = payload == 1
		elif "/vessel/0/sensor/3" in topic:
			deck_sensor_clear = payload == 0
		elif "/vessel/0/barrier/0" in topic:
			if payload == 1:
				# TODO check if warning_lights off topic is sent 4 seconds later
				if deck_open:
					log_warning("not allowed to open barriers, deck is still open");
			elif payload == 0:
				# TODO check if deck open topic is sent 4 seconds later
				if not vessel_warning_lights_on:
					log_warning("not allowed to close barriers, warning_lights are not on")
				if not deck_sensor_clear:
					log_warning("not allowed to close barriers, deck is not cleared")
			bridge_barriers_open = payload == 1
		elif "/vessel/0/sensor/1" in topic:
			under_deck_sensor_clear = payload == 0
		elif "/vessel/0/deck/0" in topic:
			if payload == 1:
				# TODO check if a boat_light green topic is sent 10 seconds later
				if bridge_barriers_open:
					log_warning("not allowed to open deck when barriers are open")
				if not deck_sensor_clear:
					log_warning("not allowed to open deck when it`s not cleared")
				if not vessel_warning_lights_on:
					log_warning("not allowed to open deck when warning_lights are off")
			elif payload == 0:
				# TODO check if barriers open topic is sent 10 seconds later
				if boat_light_0_green or boat_light_1_green:
					log_warning("not allowed to close deck when boat_light is green")
				if not under_deck_sensor_clear:
					log_warning("not allowed to close deck when there are vessels under it")
					
			deck_open = payload == 1

