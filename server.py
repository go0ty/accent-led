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

led_count = 72
strip = init_led(led_count)

app = Flask(__name__)

@app.route('/')
def healthCheck():
	return 'Up.'

@app.route('/color/<string:color>', methods=['PUT'])
def changeColor(color):
	for x in range(led_count):
		strip.setPixelColor(x, int(color), 16)
	return flask.Response(status=200)