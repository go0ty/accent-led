#!/usr/bin/python
#
# Main LED loop that pushes LED Zones to the Accent Server
import sys
import argparse
import colorsys
import requests
from mss import mss

def parse_args(args):
	# Getting command line arguments
	parser = argparse.ArgumentParser(description="Accent LED Client")
	parser.add_argument("--server", type=str, help="The IP address of the server")
	parser.add_argument("--monitor", type=int, help="The monitor to capture")
	return parser.parse_args(args)

def main_loop(args):
	print("Connecting to {} on monitor {}.".format(args.server, args.monitor))
	response = requests.get("http://{}/".format(args.server))
	if response.status_code != 200:
		print("Couldn't connect to server.", timeout=1)
		exit()
	print("Connected to server.")

	while True:
		pass

if __name__ == "__main__":
	# Parse Arguments
	parsed_args = parse_args(sys.argv[1:])
	# Begin main LED Loop
	main_loop(parsed_args)
