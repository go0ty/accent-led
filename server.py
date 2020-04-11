#!/usr/bin/python
#
# Server that handles color requests from the clients.
#
import threading
import time
import colorsys
from flask import Flask
from dotstar import Adafruit_DotStar

# Startup the LED
def init_led(num_pixels):
	global strip
	strip = Adafruit_DotStar(num_pixels, 12000000)
	strip.begin()
	strip.setBrightness(48)
	return strip

# Setup LED Strip globals
num_pixels = 72
strip = init_led(num_pixels)
target_hue = None
current_hue = None

# Chases a target Hue with the LED, for graceful color transitioning
def background_hue_chase():
	global current_hue
	global target_hue
	global num_pixels
	step = 3
	pause = 0.03

	while True:
		# If there's no Target, then do nothing.
		if target_hue is None:
			time.sleep(pause)
			continue

		# Update the current Hue
		if current_hue is not None:
			# If the hues are within the step, then pass to the next iteration.
			if abs(target_hue - current_hue) <= step:
				time.sleep(pause)
				continue

			# Get the three values on the Hue line (two extending, one actual)
			# to determine the fastest path to the target hue.
			target_hue_spread = [target_hue - 360, target_hue, target_hue + 360]
			closest_hue_index = None
			best_difference = None

			for index, target_hue_point in enumerate(target_hue_spread):
				difference = abs(target_hue_point - current_hue)
				if best_difference is None:
					closest_hue_index = index
					best_difference = difference
				else:
					if difference < best_difference:
						closest_hue_index = index
						best_difference = difference

			closest_target_hue = target_hue_spread[closest_hue_index]

			if current_hue > closest_target_hue:
				current_hue = current_hue - step
			elif current_hue < closest_target_hue:
				current_hue = current_hue + step
		else:
			# Ensure we have a default Hue set up
			current_hue = target_hue

		# Ensure we haven't gone outside the Hue ranges
		if current_hue > 360:
			current_hue = current_hue - 360
		if current_hue < 0:
			current_hue = current_hue + 360

		# Set the Hex for the HSL
		rgb = colorsys.hls_to_rgb(float(current_hue)/360, 0.5, 1.0)
		red = float(rgb[0]) * 255
		green = float(rgb[1]) * 255
		blue = float(rgb[2]) * 255
		color = '%02x%02x%02x' % (int(green), int(red), int(blue))

		# Update the Strip
		for x in range(num_pixels):
			strip.setPixelColor(x, int(color, 16))
		strip.show()

		# Wait until the next iteration
		time.sleep(pause)
		continue

# Start the Hue Thread
hue_chase_thread = threading.Thread(name='hue_chase', target=background_hue_chase)
hue_chase_thread.start()

# Flask
app = Flask(__name__)

@app.route('/')
def health_check():
	# Health check
	return 'OK'

@app.route('/hue/<int:color>', methods=['PUT'])
def change_targe_hue(color):
	global target_hue
	target_hue = color
	return 'OK'

@app.route('/color/<string:color>', methods=['PUT'])
def change_color(color):
	# Set every LED of the strip to a single color
	for x in range(num_pixels):
		strip.setPixelColor(x, int(color, 16))
	strip.show()
	return 'OK'
