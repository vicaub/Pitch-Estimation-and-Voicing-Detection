# -*- coding: utf8 -*-

"""
Simple pitch estimation
"""

from __future__ import print_function, division
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate, hamming
from sklearn.externals import joblib


#################### UTILITIES ############################


def get_class(zero_crossing, energy, r1, rmax):
    """
    Arbitrary rules to get the class of the frame with the features
    """
    if rmax < 0.5:
        return False
    elif zero_crossing > 0.3:
        return False
    elif r1 < 0.5:
        return False
    else:
        return True
    
    
def get_zero_crossing(frame):
    """
    Computes zero crossing rate of frame
    """
    count = len(frame)
    countZ = np.sum(np.abs(np.diff(np.sign(frame)))) / 2
    return (np.float64(countZ) / np.float64(count-1.0))

def get_energy(frame):
    """
    Computes signal energy of frame
    """
    return np.log10(np.sum(frame ** 2) / np.float64(len(frame)))

def get_autocorr(frame):
    frame = frame.astype(np.float)
    frame -= frame.mean()
    amax = np.abs(frame).max()
    frame /= amax
    defvalue = (0.0, 1.0)
    corr = correlate(frame, frame)
    # keep the positive part
    corr = corr[round(len(corr)/2):]

    # Find the first minimum
    dcorr = np.diff(corr)
    rmin = np.where(dcorr > 0)[0]
    if len(rmin) > 0:
        rmin1 = rmin[0]
    else:
        return defvalue

    # Find the next peak
    peak = np.argmax(corr[rmin1:]) + rmin1

    # Two features
    r1=corr[1]/corr[0]
    rmax = corr[peak]/corr[0]

    return r1, rmax

def preprocess_frame(frame):
    """
    Apply some treatment to the frame to make it easier to process
    """
    frame = frame.astype(np.float)
    frame -= frame.mean() # center
    amax = np.abs(frame).max()
    frame /= amax # normalize
    return frame


##################### PITCH ALGORITHMS #########################

def autocorr_method(frame, sample_rate):
    """
    Estimate pitch using autocorrelation and predefined coefficient threshold for voicing determination
    """
    corr = correlate(frame, frame)
    # keep the positive part
    corr = corr[len(corr)//2:]

    # Find the first minimum
    dcorr = np.diff(corr)
    rmin = np.where(dcorr > 0)[0]
    if len(rmin) > 0:
        rmin1 = rmin[0]
    else:
        return 0

    # Find the next peak
    peak = np.argmax(corr[rmin1:]) + rmin1
    rmax = corr[peak]/corr[0]
    f0 = sample_rate / peak

    if rmax > 0.5 and f0 > 50 and f0 < 400:
        return f0
    else:
        return 0

def mdf_method(frame, sample_rate):
    """
    estimate the pitch using mdf algorithm and machine learning model for prediction
    """
    zero_crossing = get_zero_crossing(frame)
    energy = get_energy(frame)
    r1, rmax = get_autocorr(frame)
    predicted_class = get_class(zero_crossing, energy, r1, rmax)

    if not predicted_class:
        # it's unvoiced, no need to compute pitch
        return 0

    minValue = float("inf")
    minArg = 0
    kmin = int(sample_rate / 350)
    kmax = int(sample_rate / 100)
    n = len(frame)

    for k in range(kmin, kmax):

        mdf = np.sum(np.absolute(frame - np.roll(frame, k)))

        # amdf = mdf / n - 1 - k
            
        # if amdf < minValue:
        #     minValue = amdf
        #     minArg = k

        if mdf < minValue:
            minValue = mdf
            minArg = k    

    return sample_rate / minArg


def cepstrum_method(frame, sample_rate):
    """
    Perform pitch estimation with cepstrum method and machine learning model for prediction
    """
    zero_crossing = get_zero_crossing(frame)
    energy = get_energy(frame)
    r1, rmax = get_autocorr(frame)
    predicted_class = get_class(zero_crossing, energy, r1, rmax)

    if not predicted_class:
        # it's unvoiced, no need to compute pitch
        return 0

    # Normalize the frame to -1 to 1
    frame = frame/np.max(frame)
    N = len(frame)
    noise = (np.random.random_sample(N)-.5)*.05
    frame = frame+noise
    
    # Apply a window to the frame
    windowed_frame = frame*hamming(N)
    # Compute ceptrsum
    cepstrum = np.abs(np.fft.irfft(np.log(np.abs(np.fft.rfft(windowed_frame)))))
    start = int(N/12)
    end = int(N/2)
    
    # Find the highest peak and interpolate to get a more accurate result
    peak = np.argmax(cepstrum[start:end])
    
    # Convert to the corresponding frequency
    f0 = sample_rate/(start+peak)
    
    if f0 > 100 and f0 < 400:
        return f0
    else:
        return 0


############################## FILE LOADING ##############################################

def getwav_files(options, gui):
    """
    Locate, open and extract the wav files
    Return a list of all the wav samples with their sample rate and data list
    """
    wav_files = []
    with open(gui) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            file_name = os.path.join(options.datadir, line + ".wav")
            sample_rate, data = wavfile.read(file_name)

            nSamples = len(data)

            # From miliseconds to samples
            ns_windowlength = int(round((options.windowlength * sample_rate) / 1000))
            ns_frameshift = int(round((options.frameshift * sample_rate) / 1000))
            ns_padding = int(round((options.padding * sample_rate) / 1000))

            frames = []
            for ini in range(-ns_padding, nSamples - ns_windowlength + ns_padding + 1, ns_frameshift):
                first_sample = max(0, ini)
                last_sample = min(nSamples, ini + ns_windowlength)
                frame = data[first_sample:last_sample]
                # make preprocessing here
                frame = preprocess_frame(frame)
                frames.append(frame)

            wav_files.append({"file_name": file_name, "sample_rate": sample_rate, "frames": frames})
    return np.array(wav_files)

def main(options, args):
    """
    Main script function
    """
    # get the wav files
    wav_files = getwav_files(options, args[0])

    # print the algorithm name at the top of the directory
    header_file = os.path.join(os.path.dirname(wav_files[0]["file_name"]), "algorithm.info")
    with open(header_file, 'wt') as header_file:
        print(options.method, file=header_file)

    for wav_file in wav_files:
        f0_file_name = wav_file["file_name"].replace(".wav", ".f0")
        with open(f0_file_name, 'wt') as f0file:
            print("Processing:", wav_file["file_name"], "with", options.method, '->', f0_file_name)
            for frame in wav_file["frames"]:
                # compute the pitch for each frame
                f0 = 0
                if options.method == "autocorrelation":
                    f0 = autocorr_method(frame, wav_file["sample_rate"])
                elif options.method == "mdf":
                    f0 = mdf_method(frame, wav_file["sample_rate"])
                elif options.method == "cepstrum":
                    f0 = cepstrum_method(frame, wav_file["sample_rate"])
                
                # print the result in the new file
                print(f0, file=f0file)


if __name__ == "__main__":
    import optparse
    optparser = optparse.OptionParser(
        usage='python3 %prog [OPTION]... FILELIST\n' + __doc__)
    optparser.add_option(
        '-w', '--windowlength', type='float', default=32,
        help='windows length (ms)')
    optparser.add_option(
        '-f', '--frameshift', type='float', default=15,
        help='frame shift (ms)')
    optparser.add_option(
        '-p', '--padding', type='float', default=16,
        help='zero padding (ms)')
    optparser.add_option(
        '-d', '--datadir', type='string', default='data',
        help='data folder')
    optparser.add_option(
        '-m', '--method', type='string', default='mdf',
        help='pitch detection method: autocorrelation, cepstrum or mdf (default)')

    options, args = optparser.parse_args()

    if options.method:
        if options.method not in ["autocorrelation", "cepstrum", "mdf"]:
            print("The method {} is not valid".format(options.method))
            optparser.print_help()
            exit(-1)

    if len(args) == 0:
        print("No FILELIST provided")
        optparser.print_help()
        exit(-1)

    main(options, args)
