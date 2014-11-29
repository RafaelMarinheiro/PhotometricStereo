#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: marinheiro
# @Date:   2014-09-23 17:33:09
# @Last Modified by:   marinheiro
# @Last Modified time: 2014-09-23 19:56:02

import util
import argparse
import numpy as np
from PIL import Image
import scipy.misc
from scipy import linalg

def compute_normals(light_matrix, mask_array, images_array, threshold=100):
	shap = mask_array.shape
	shaper = (shap[0], shap[1], 3)

	normal_map = np.zeros(shaper)
	ivec = np.zeros(len(images_array))

	for (xT, value) in np.ndenumerate(mask_array):
		if(value > threshold):
			for (pos, image) in enumerate(images_array):
				ivec[pos] = image[xT[0], xT[1]]

			(normal, res, rank, s) = linalg.lstsq(light_matrix, ivec)

			normal = normal/linalg.norm(normal)

			if not np.isnan(np.sum(normal)):
				normal_map[xT] = normal

	return normal_map

def compute_albedo(light_matrix, mask_array, images_array, normal_map, threshold=100):
	shap = mask_array.shape
	shaper = (shap[0], shap[1], 3)

	albedo_map = np.zeros(shaper)
	ivec = np.zeros((len(images_array), 3))

	for (xT, value) in np.ndenumerate(mask_array):
		if(value > threshold):
			for (pos, image) in enumerate(images_array):
				ivec[pos] = image[xT[0], xT[1]]

			i_t = np.dot(light_matrix, normal_map[xT])

			k = np.dot(np.transpose(ivec), i_t)/(np.dot(i_t, i_t))

			if not np.isnan(np.sum(k)):
				albedo_map[xT] = k

	return albedo_map

def simple_photometric_stereo(images_files, mask_image_file, lights_file, threshold=25):
	lights = util.read_lights_file(lights_file)
	mask_image = Image.open(mask_image_file)
	mask_image_gray = mask_image.convert("L")
	mask_image_array = scipy.misc.fromimage(mask_image_gray)
	# print mask_image_array

	images = []
	images_array = []
	images_gray = []
	images_gray_array = []

	for image_file in images_files:
		image = Image.open(image_file)
		image_array = scipy.misc.fromimage(image)
		image_gray = image.convert("L")
		# image_gray.show()

		image_gray_array = scipy.misc.fromimage(image_gray)
		# print image_array

		images.append(image)
		images_array.append(image_array)
		images_gray.append(image_gray)
		images_gray_array.append(image_gray_array)

	normal_map = compute_normals(np.array(lights), mask_image_array, images_gray_array)
	albedo_map = compute_albedo(np.array(lights), mask_image_array, images_array, normal_map)


	return (normal_map, albedo_map)

def main(args):
	ret = util.read_header_file(args.header)
	data = simple_photometric_stereo(ret["images"], ret["mask"], args.lights_file)

	normal_map = scipy.misc.toimage(data[0])
	albedo_map = scipy.misc.toimage(data[1])

	normal_map.save(args.output_format % "normal")
	albedo_map.save(args.output_format % "albedo")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("header")
	parser.add_argument("lights_file")
	parser.add_argument("output_format")
	args = parser.parse_args()
	main(args)