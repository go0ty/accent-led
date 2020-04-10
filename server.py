#!/usr/bin/python
#
# Server that handles color requests from the clients.
import sys
import argparse
import colorsys
from flask import Flask
from dotstar import Adafruit_DotStar

# Startup the LED
def init_led(numPixels):
	strip = Adafruit_DotStar(numPixels, 12000000)
	strip.begin()
	strip.setBrightness(32)
	return strip

num_pixels = 72
strip = init_led(num_pixels)

app = Flask(__name__)

@app.route('/')
def healthCheck():
	return 'OK'

@app.route('/color/<string:color>', methods=['PUT'])
def changeColor(color):
	for x in range(num_pixels):
		strip.setPixelColor(x, int(color, 16))
	strip.show()
	return 'OK'