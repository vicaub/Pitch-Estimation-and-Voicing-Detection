# Pitch Estimation and Voicing Detection

## Installation

Download the FDA-UE database to test the script and optionnaly the PTDB-TUB database to train the model (see below)

You need Python 3
Install the Python dependencies
```
$ pip3 install -r requirements.txt  
```

Compile the program
```
$ Make
```


## How to use it

Execute the pitch recognition script with choosing an algorithm
```
Usage: python3 get_pitch.py [OPTION]... FILELIST

Simple pitch estimation

Options:
  -h, --help            show this help message and exit
  -w WINDOWLENGTH, --windowlength=WINDOWLENGTH
                        windows length (ms)
  -f FRAMESHIFT, --frameshift=FRAMESHIFT
                        frame shift (ms)
  -p PADDING, --padding=PADDING
                        zero padding (ms)
  -d DATADIR, --datadir=DATADIR
                        data folder
  -m METHOD, --method=METHOD
                        pitch detection method: autocorrelation, cepstrum or
                        mdf (default)
```

Then you can use the c++ script to compare the results with the reference
````
./compare_pitch fda_ue.gui
````

It will generate a file in ./results folder showing 

    Voiced frames -> unvoiced (1 - recall voiced)
    Number of unvoiced frames that have been erroneously classified as voiced.
    Unvoiced frames -> voiced: (1 - recall unvoiced)
    Number of voiced frames that have been erroneously classified as unvoiced.
    Gross voiced errors:
    In voiced frames, detected as voiced,
    Pitch errors greater than 20%
    MSE of fine errors:
    In voiced frames, detected as voiced with an error less than 20%,
    the average of that error. (Mean Squared Error)
     
It also provides a summary with the average over all files.


```
./pitch_compare fda_ue.gui

### Summary
Num. frames:	22140 = 13916 unvoiced + 8224 voiced
Unvoiced frames as voiced:	309/13916 (2.2%)
Voiced frames as unvoiced:	1661/8224 (20%)
Gross voiced errors (+20%):	30/6563 (0.46%)
MSE of fine errors:	2%
```

You can also execute all the three available algorithm and the comparison with the command
```
source test.sh
```
## Clean pitch results

You can clean the computed pitchs for all algorithm located in data/fda_ue with the script clean_results/sh

```
source clean_results/sh
```

## Source code license ##
* The source code of this project is licensed under the terms of the MIT license

## Detailed information about the databases ##
* More details about the FDA-UE database can be found in http://www.cstr.ed.ac.uk/research/projects/fda/
* More details about the PTDB-TUB database can be found in G. Pirker, M. Wohlmayr, S. Petrik, and F. Pernkopf. ["A Pitch Tracking Corpus with Evaluation on Multipitch Tracking Scenario"](https://www.spsc.tugraz.at/system/files/InterSpeech2011Master_0.pdf), Interspeech, pp. 1509-1512, 2011.  
The PTDB-TUG Database is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/  
Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/ Please cite the above given reference when using the database. 
