#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: marinheiro
# @Date:   2014-09-23 14:36:29
# @Last Modified by:   marinheiro
# @Last Modified time: 2014-09-23 17:26:08

from PIL import Image

import util
import argparse
import numpy
import scipy.misc
import math

def filterF(a, threshold):
	if a > threshold:
		return (255, 0, 0, 0)
	else:
		return (0, 0, 0, 0)

def compute_centroid(im_array, threshold=100):
	tot = 0.0
	xS = 0
	yS = 0
	for (x,value) in numpy.ndenumerate(im_array):
		if value > threshold:
			xS = xS + x[0]
			yS = yS + x[1]
			tot = tot+1

	return (xS/tot, yS/tot) 

def compute_radius(im_array, centroid, threshold=100):
	r = 0

	for (xT, value) in numpy.ndenumerate(im_array):
		if value > threshold:
			r = max(r, math.sqrt((xT[0]-centroid[0])**2 + (xT[1]-centroid[1])**2))

	return r


def compute_light_directions(images_files, mask_image_file):
	mask_image = Image.open(mask_image_file)
	mask_image_gray = mask_image.convert("L")
	mask_image_array = scipy.misc.fromimage(mask_image_gray)
	mask_centroid = compute_centroid(mask_image_array)
	mask_radius = compute_radius(mask_image_array, mask_centroid)

	light_directions = []
	for image_file in images_files:
		image = Image.open(image_file)
		image_gray = image.convert("L")
		# image_gray.show()
		image_array = scipy.misc.fromimage(image_gray)
		centroid = compute_centroid(image_array)
		# print image_file
		# print centroid
		# print mask_centroid

		r = mask_radius
		dx = centroid[1]-mask_centroid[1]
		dy = centroid[0]-mask_centroid[0]
		dy = -dy

		N = numpy.array([dx/r,
						 dy/r,
						 math.sqrt(r*r - dx*dx - dy*dy)/r])
		
		R = numpy.array([0, 0, 1])
		L = 2*numpy.dot(N, R)*N - R
		light_directions.append(L)

	return light_directions


def main(args):
	ret = util.read_header_file(args.header)
	light_directions = compute_light_directions(ret['images'], ret['mask'])

	with open(args.output_file, 'w') as output_file:
		output_file.write('Header: %s\n'%args.header)
		output_file.write('%d\n'%len(light_directions))
		for light in light_directions:
			output_file.write('%lf %lf %lf\n' % (light[0], light[1], light[2]))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("header")
	parser.add_argument("output_file")
	args = parser.parse_args()
	main(args)