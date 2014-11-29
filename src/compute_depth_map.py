#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: marinheiro
# @Date:   2014-09-24 00:57:44
# @Last Modified by:   marinheiro
# @Last Modified time: 2014-10-02 17:22:08

import util
import argparse
import numpy as np
from PIL import Image
import scipy.misc, scipy.sparse
import scipy.sparse.linalg
from scipy import linalg


from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def compute_depth(mask_array, normal_array, threshold=100):
	index_map = -np.ones(mask_array.shape)

	x = []
	y = []
	ind = 0
	for (xT, value) in np.ndenumerate(mask_array):
		if(value > threshold):
			index_map[xT] = ind
			x.append(xT[1])
			y.append(-xT[0])
			ind = ind+1

	row = []
	col = []
	data = []
	b = []

	i = 0
	for (xT, value) in np.ndenumerate(index_map):
		if value >= 0:
			normal = normal_array[xT]/128.0 - 1.0
			normal = normal/linalg.norm(normal)


			if not np.isnan(np.sum(normal)):
				#x
				iother = index_map[xT[0], xT[1]+1]
				if abs(normal[2]) > 0.01:
					if iother >= 0:
						row.append(i)
						col.append(value)
						data.append(-normal[2])
						row.append(i)
						col.append(iother)
						data.append(normal[2])
						b.append(-normal[0])
						i = i+1


					#y
					iother = index_map[xT[0]-1, xT[1]]
					if iother >= 0:
						row.append(i)
						col.append(value)
						data.append(-normal[2])
						row.append(i)
						col.append(iother)
						data.append(normal[2])
						b.append(-normal[1])
						i = i+1


	mat = scipy.sparse.coo_matrix((data, (row, col)), shape=(i, ind)).tocsc()
	b = np.array(b)

	z = scipy.sparse.linalg.lsqr(mat,b, iter_lim=1000, show=True)
	
	ind = 0
	for (xT, value) in np.ndenumerate(index_map):
		if value >= 0:
			index_map[xT] = z[0][ind]
			ind = ind+1

	return index_map
			
	




def run_compute_surface(mask_image, normal_map_image):
	mask_image = Image.open(mask_image)
	mask_image_gray = mask_image.convert("L")
	mask_image_array = scipy.misc.fromimage(mask_image_gray)
	
	normal_image = Image.open(normal_map_image)
	# normal_image.show()
	normal_array = scipy.misc.fromimage(normal_image)
	# print mask_image_array

	depth_map = compute_depth(mask_image_array, normal_array)
	return depth_map

def main(args):
	ret = util.read_header_file(args.header)
	data = run_compute_surface(ret['mask'], args.normal_map)

	depth_map = scipy.misc.toimage(data)
	# albedo_map = scipy.misc.toimage(data[1])

	depth_map.save(args.output_format % "depth")
	# albedo_map.save(args.output_format % "albedo")

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("header")
	parser.add_argument("normal_map")
	parser.add_argument("output_format")
	args = parser.parse_args()
	main(args)