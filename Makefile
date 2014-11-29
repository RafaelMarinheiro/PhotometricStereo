compute_light = src/compute_light_directions.py
calibrated_photometric = src/simple_photometric_stereo.py
uncalibrated_photometric = src/unknown_light_photometric_stereo.py
compute_depth = src/compute_depth_map.py

objects = buddha cat gray horse owl rock

my_phony_targets = all
# my_phony_targets += $(addsuffix .stereo, $(objects))
# my_phony_targets += $(addsuffix .calibrated_normal, $(objects))
# my_phony_targets += $(addsuffix .uncalibrated_normal, $(objects))
# my_phony_targets += $(addsuffix .calibrated_depth, $(objects))
# my_phony_targets += $(addsuffix .uncalibrated_depth, $(objects))

.PHONY: all all_calibrated_normal all_calibrated_depth lights clean

%.calibrated_normal: lights
	python $(calibrated_photometric) images/$*/$*.txt output/lights.txt output/calibrated_$*_%s.png

%.uncalibrated_normal: $(uncalibrated_photometric)
	python $(uncalibrated_photometric) images/$*/$*.txt output/uncalibrated_$*_%s.png

%.calibrated_depth: $(compute_depth)
	python $(compute_depth) images/$*/$*.txt output/calibrated_$*_normal.png output/calibrated_$*_%s.png

%.uncalibrated_depth: $(compute_depth)
	python $(compute_depth) images/$*/$*.txt output/uncalibrated_$*_normal.png output/uncalibrated_$*_%s.png

%.stereo: $*.calibrated_depth $*.uncalibrated_depth
	echo HI

all_calibrated_normal: $(addsuffix .calibrated_normal, $(objects))

all_uncalibrated_normal: $(addsuffix .uncalibrated_normal, $(objects))

all_calibrated_depth: all_calibrated_normal $(addsuffix .calibrated_depth, $(objects))

all_uncalibrated_depth: all_uncalibrated_normal $(addsuffix .uncalibrated_depth, $(objects))

all: all_calibrated_depth all_uncalibrated_depth

clean:
	rm -rf output/*

lights: output/lights.txt

output/lights.txt: $(compute_light)
	python $(compute_light) images/chrome/chrome.txt $@