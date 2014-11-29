Check the requirements:
	1) Python 2.7
	2) pip (http://pip.readthedocs.org/en/latest/installing.html)
	3) If pip is installed, run
			pip install -r requirements.txt
	   to install the rest of the requirements (PIL, numpy and scipy)

Running:
	
	First, create a folder called output:
		mkdir output

	This package has 4 executables:

	1) 	src/compute_light_directionts.py
	   	How to use it:

	   	Run
	   		python src/compute_light_directions.py images/chrome/chrome.txt output/lights.txt

	   	to compute the light directions

	2)	src/simple_photometric_stereo.py
		How to use it:

		Run
			python src/simple_photometric_stereo.py images/<TEST>/<TEST>.txt
			output/lights.txt output/calibrated_<TEST>_%s.png

		to compute the albedo and normal using the calibrated photometric stereo

	3)	src/unknown_light_photometric_stereo.py
		How to use it:

		Run
			python src/unknown_light_photometric_stereo.py images/<TEST>/<TEST>.txt output/calibrated_<TEST>_%s.png

		to compute the albedo and normal using the uncalibrated photometric stereo

	4) 	1) 	src/compute_light_directionts.py
	   	How to use it:

	   	Run
	   		python src/compute_light_directions.py images/<TEST>/<TEST>.txt output/(calibrated|uncalibrated)_<TEST>_normal.png output/(calibrated|uncalibrated)_<TEST>_%s.png

	   	to compute the depth map

	For convenience, you can simply run
		make all
	to run all the test cases. The result will be in the output_folder.





