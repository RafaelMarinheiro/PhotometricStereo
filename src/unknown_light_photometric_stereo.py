#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: marinheiro
# @Date:   2014-09-23 22:45:15
# @Last Modified by:   marinheiro
# @Last Modified time: 2014-10-05 00:52:05

import util
import argparse
import numpy as np
from PIL import Image
import scipy.misc
from scipy import linalg
import math

def compute_normals_and_lights(mask_array, images_array, threshold=100):
	shap = mask_array.shape
	shaper = (shap[0], shap[1], 3)

	normal_map = np.zeros(shaper)
	ivec = np.zeros(len(images_array))

	M = None

	for image in images_array:
		arr = []
		for (xT, value) in np.ndenumerate(mask_array):
			if(value > threshold):
				arr.append(image[xT]/255.0)

		if M == None:
			M = np.array(arr)
		else:
			M = np.vstack((M, np.array(arr)))

	(U, s, Vh) = linalg.svd(M, full_matrices=False)

	L = U[:,0:3]
	N = Vh[0:3,:]
	S_sqrt = np.diag(np.sqrt(s[:3]))
	L = np.dot(L, S_sqrt)
	N = np.dot(S_sqrt, N)

	L_help = None
	for i in range(L.shape[0]):
		x = L[i, 0]
		y = L[i, 1]
		z = L[i, 2]
		arr = [x*x, 2*x*y, 2*x*z, y*y, 2*y*z, z*z]

		if L_help == None:
			L_help = np.array(arr)
		else:
			L_help = np.vstack((L_help, arr))

	(b_p, res, rank, s) = linalg.lstsq(L_help, np.ones(L.shape[0]))

	B = np.array([[b_p[0], b_p[1], b_p[2]],
				  [b_p[1], b_p[3], b_p[4]],
				  [b_p[2], b_p[4], b_p[5]]])

	(U, s, Vh) = linalg.svd(B)
	A = np.dot(U, np.diag(np.sqrt(s)))

	L = np.dot(L, A)
	N = linalg.solve(A, N)

	Rot = np.array([[1,  0, 0],
					[0, 1, 0],
					[0, 0, 1]])

	# Rot = np.array([[0,  0, 1],
	# 				[0, -1, 0],
	# 				[-1, 0, 0]])

	# # Rot = np.dot(Rot,
	# # 			np.array([[0, 1, 0],
	# # 					  [1, 0, 0],
	# # 					  [1, 0, 1]]))


	# Rot = np.dot(Rot,
	# 			np.array([[0.5, -math.sqrt(3.0)/2, 0],
	# 					  [0, 0, 1],
	# 					  [math.sqrt(3.0)/2, 0.5, 0]]))


	L = np.dot(L, Rot)
	N = linalg.solve(Rot, N) 

	i = 0
	for (xT, value) in np.ndenumerate(mask_array):
		if(value > threshold):
			normal = N[:, i]
			# normal = np.array([normal[2], normal[1], -normal[0]])
			normal = normal/linalg.norm(normal)
			if not np.isnan(np.sum(normal)):
				normal_map[xT] = normal

			i = i+1

	return (normal_map, L)


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

def unknown_light_photometric_stereo(images_files, mask_image_file, threshold=25):
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

	(normal_map, light_matrix) = compute_normals_and_lights(mask_image_array, images_gray_array)
	albedo_map = compute_albedo(light_matrix, mask_image_array, images_array, normal_map)


	return (normal_map, albedo_map)

def main(args):
	ret = util.read_header_file(args.header)
	data = unknown_light_photometric_stereo(ret["images"], ret["mask"])

	normal_map = scipy.misc.toimage(data[0])
	albedo_map = scipy.misc.toimage(data[1])

	normal_map.save(args.output_format % "normal")
	albedo_map.save(args.output_format % "albedo")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("header")
	# parser.add_argument("lights_file")
	parser.add_argument("output_format")
	args = parser.parse_args()
	main(args)