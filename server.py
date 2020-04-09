#!/usr/bin/python
#
# Server that handles color requests from the clients.
import sys
import argparse
import colorsys
from flask import Flask
from dotstar import Adafruit_DotStar

app = Flask(__name__)

@app.route('/')
def healthCheck():
	return 'Healthy.'

@app.route('/color/<color>', methods=['PUT'])
def changeColor(color):
	return flask.Response(status=200)