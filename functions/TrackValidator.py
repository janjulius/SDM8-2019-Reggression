from helpers import check_statement
from cust_logging import log_warning
from threading import Thread, Timer

class TrackValidator:
	track_barriers_open = True
	crossing_clear = True
	track_east_clear = True
	track_west_clear = True
	track_warning_lights_on = False
	track_light_0_green = False
	track_light_1_green = False


	def validate(self, topic, payload):
		if "/track/0/train_light/0" in topic:
			self.track_light_0_green = payload == 1
		elif "/track/0/train_light/1" in topic:
			self.track_light_1_green = payload == 1;
		elif "/track/0/warning_light/0" in topic:
			if payload == 0:
				if not self.track_barriers_open:
					log_warning(f'cannot turn of warning_light, barriers are closed')
			if payload == 1:
				
				if self.track_west_clear and self.track_east_clear:
					log_warning(f'not allowed to turn on warning_light when no train is coming')

				# check if barriers close topic is sent 5 seconds later

			
			self.track_warning_lights_on = payload == 1
		elif "/track/0/sensor/0" in topic:
			if payload == 1:
				# check if warning_lights on topic is sent
				Timer(1.5, check_statement, [
					lambda: self.track_warning_lights_on,
					"train is coming, warning lights should go on",
					topic
					]).start()
				
			self.track_east_clear = payload == 0
		elif "/track/0/sensor/1" in topic:
			self.crossing_clear = payload == 0
		elif "/track/0/sensor/2" in topic:
			if payload == 1:
				# check if warning_lights on topic is sent
				Timer(1.5, check_statement, [
					lambda: self.track_warning_lights_on,
					"train is coming, warning lights should go on",
					topic
					]).start()
				
			self.track_west_clear = payload == 0;
		elif "/track/0/barrier/0" in topic:
			if payload == 1: 
				if not self.track_warning_lights_on:
					log_warning(f'cannot close barrier, when warning lights are off');
					
				# check if track_light 0 or 1 green is sent 4 seconds later
				Timer(4.5, check_statement, [
					lambda: self.track_light_0_green or self.track_light_1_green,
					"train light can be turned on",
					topic
					]).start()
				
			if payload == 0:
				if not self.crossing_clear or not self.track_east_clear or not self.track_west_clear:
					log_warning(f'cannot open barrier, track not clear');
					
				# check if warning_lights off topic is sent 4 seconds later
				Timer(4.5, check_statement, [
					lambda: self.track_warning_lights_on,
					"track warning_lights should be off",
					topic
					]).start()
				
			self.track_barriers_open = payload == 1