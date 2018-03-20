#!/bin/bash

g++ compare_pitch.cpp -o compare_pitch

source clean_results.sh

python3 get_pitch.py -m cepstrum fda_ue.gui

./compare_pitch fda_ue.gui

python3 get_pitch.py -m autocorrelation fda_ue.gui

./compare_pitch fda_ue.gui

python3 get_pitch.py -m mdf fda_ue.gui

./compare_pitch fda_ue.gui
