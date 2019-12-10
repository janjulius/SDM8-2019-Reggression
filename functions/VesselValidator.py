from helpers import check_statement
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

	def validate(self, topic, payload):
		if "/vessel/0/boat_light/0" in topic:
			if payload == 1 and not self.deck_open:
				log_warning("deck is closed can not turn lights green")
			self.boat_light_0_green = payload == 1
		elif "/vessel/0/boat_light/1" in topic:
			if payload == 1 and not self.deck_open:
				log_warning("deck is closed can not turn lights green")
			self.boat_light_1_green = payload == 1;
		elif "/vessel/0/warning_light/0" in topic:
			if payload == 0:
				if self.deck_open:
					log_warning("not allowed to turn off warning_light when deck is open");
				if not self.bridge_barriers_open:
					log_warning("not allowed to turn off warning_light, barriers are still closed");
			self.vessel_warning_lights_on = payload == 1
		elif "/vessel/0/sensor/3" in topic:
			self.deck_sensor_clear = payload == 0
		elif "/vessel/0/barrier/0" in topic:
			if payload == 1:
				if not self.vessel_warning_lights_on:
					log_warning("not allowed to close barriers, warning_lights are not on")
				if not self.deck_sensor_clear:
					log_warning("not allowed to close barriers, deck is not cleared")
				# check if deck open topic is sent 4 seconds later
				Timer(4.5, check_statement, [
					lambda: not self.deck_open,
					"barriers have been closed, deck should open",
					topic
					]).start()
			elif payload == 0:
				if self.deck_open:
					log_warning("not allowed to open barriers, deck is still open");
				# check if warning_lights off topic is sent 4 seconds later
				Timer(4.5, check_statement, [
					lambda: self.vessel_warning_lights_on,
					"barriers have been opened, warning_light should be off",
					topic
					]).start()
			self.bridge_barriers_open = payload == 1
		elif "/vessel/0/sensor/1" in topic:
			self.under_deck_sensor_clear = payload == 0
		elif "/vessel/0/deck/0" in topic:
			if payload == 1:
				if self.bridge_barriers_open:
					log_warning("not allowed to open deck when barriers are open")
				if not self.deck_sensor_clear:
					log_warning("not allowed to open deck when it`s not cleared")
				if not self.vessel_warning_lights_on:
					log_warning("not allowed to open deck when warning_lights are off")
				# check if a boat_light green topic is sent 10 seconds later
				Timer(10.5, check_statement, [
					lambda: not self.boat_light_0_green and not self.boat_light_1_green,
					"deck is open, a boat_light should be turned on",
					topic
					]).start()
			elif payload == 0:
				if self.boat_light_0_green or self.boat_light_1_green:
					log_warning("not allowed to close deck when boat_light is green")
				if not self.under_deck_sensor_clear:
					log_warning("not allowed to close deck when there are vessels under it")
				# check if barriers open topic is sent 10 seconds later
				Timer(10.5, check_statement, [
					lambda: not self.bridge_barriers_open,
					"deck is closed, barriers should have been opened",
					topic
					]).start()
					
			self.deck_open = payload == 1