#!/usr/bin/python
#
# Main LED loop that pushes LED Zones to the Accent Server
#
# Credit to https://adamspannbauer.github.io/2018/03/02/app-icon-dominant-colors/ for the Clustering algorithm
#
import sys
import argparse
import colorsys
import requests
import numpy
import mss
import cv2
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter

def parse_args(args):
	# Getting command line arguments
	parser = argparse.ArgumentParser(description="Accent LED Client")
	parser.add_argument("--server", type=str, help="The IP address of the server")
	parser.add_argument("--monitor", type=int, help="The monitor to capture")
	parser.add_argument("--clusters", type=int, help="The number of K-Means clusters")
	return parser.parse_args(args)

def get_monitor_image(sct, displays, monitor):
	# Capturing the monitor image
	sct.get_pixels(displays[monitor])
	image = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
	image = numpy.array(image)
	return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def find_best_color(cluster_centers, label_counts):
	non_gray_centroids = []
	for index, centroid in enumerate(cluster_centers):
		# Filter out all the centroids that represent greyscale
		centroid_average = (centroid[0] + centroid[1] + centroid[2]) / 3
		is_gray = True
		for color in centroid:
			if abs(color - centroid_average) > 40:
				is_gray = False
		if is_gray is False:
			non_gray_centroids.append({'Index': index, 'Centroid': centroid})
	if len(non_gray_centroids) >= 1:
		# Non-gray colors detected, find the best one.
		best_count = 0
		best_index = None
		for centroid in non_gray_centroids:
			count = label_counts[centroid.get('Index')]
			if count > best_count:
				best_index = centroid.get('Index')
		return cluster_centers[best_index]
	else:
		# If everything is greyscale, then let the most common cluster through.
		return cluster_centers[label_counts.most_common(1)[0][0]]

def get_boosted_hue(red, green, blue):
	hls = colorsys.rgb_to_hls(red, green, blue)
	return hls[0]

def main_loop(args):
	# Health Check
	print("Connecting to {} on monitor {}.".format(args.server, args.monitor))
	response = requests.get("http://{}/".format(args.server))
	if response.status_code != 200:
		print("Couldn't connect to server.", timeout=1)
		exit()
	print("Connected to server.")

	# Setup MSS
	sct = mss.mss()
	displays = sct.enum_display_monitors()

	while True:
		# Get Monitor Image
		image = get_monitor_image(sct, displays, int(args.monitor))
		# Resize the Image
		image = cv2.resize(image, (40, 40), interpolation = cv2.INTER_AREA)
		# Reshape the Image
		image = image.reshape((image.shape[0] * image.shape[1], 3))
		# Cluster
		clusters = KMeans(n_clusters = args.clusters, max_iter = 10)
		labels = clusters.fit_predict(image)
		label_counts = Counter(labels)

		# Get the Dominant Color
		dominant_color = find_best_color(clusters.cluster_centers_, label_counts)
		color_list = list(dominant_color)
		# Separate the RGB Values, scale 0-1
		blue = float(color_list[0])/255
		green = float(color_list[1])/255
		red = float(color_list[2])/255

		# Convert to HLS and boost values a bit
		boosted_hue = get_boosted_hue(red, green, blue)

		# Send to the API
		try:
			response = requests.put("http://{}/hue/{}".format(args.server, int(boosted_hue*360)), timeout=1)
		except:
			print("Failed to print color {}".format(boosted_hue))

if __name__ == "__main__":
	# Parse Arguments
	parsed_args = parse_args(sys.argv[1:])
	# Begin main LED Loop
	main_loop(parsed_args)
