#!/bin/bash

g++ compare_pitch.cpp -o compare_pitch

python3 get_pitch.py fda_ue.gui

./compare_pitch fda_ue.gui
