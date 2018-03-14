# -*- coding: utf8 -*-

"""
Simple pitch estimation
"""

from __future__ import print_function, division
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate, hamming



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
    return np.sum(frame ** 2) / np.float64(len(frame))

def autocorr_method(frame, sampleRate):
    """
    Estimate pitch using autocorrelation
    """
    # Calculate autocorrelation using scipy correlate
    frame = frame.astype(np.float)
    frame -= frame.mean()
    amax = np.abs(frame).max()
    if amax > 0:
        frame /= amax
    else:
        return 0

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
    f0 = sampleRate / peak

    if rmax > 0.5 and f0 > 50 and f0 < 400:
        return f0
    else:
        return 0

def amdf_method(frame, sampleRate):
    """
    estimate the pitch using mdf algorithm
    """
    energy = get_energy(frame)
    zeroCrossing = get_zero_crossing(frame)

    if zeroCrossing > 0.1 or energy < 500:
        return 0

    minValue = float("inf")
    minArg = 0
    kmin = int(sampleRate / 350)
    kmax = int(sampleRate / 100)
    n = len(frame)
    for k in range(kmin, kmax):
        i = k
        mdf = 0

        mdf = np.sum(np.absolute(np.diff(frame)))

        amdf = mdf / n - 1
            
        if amdf < minValue:
            minValue = amdf
            minArg = k
    

    return sampleRate / minArg


def cepstrum_method(frame, sampleRate):
    """
    """
    energy = get_energy(frame)
    zeroCrossing = get_zero_crossing(frame)

    if zeroCrossing > 0.1 or energy < 500:
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
    f0 = sampleRate/(start+peak)
    
    if f0 > 100 and f0 < 400:
        return f0
    else:
        return 0



def getWavFiles(options, gui):
    """
    Locate, open and extract the wav files
    Return a list of all the wav samples with their sample rate and data list
    """
    wavFiles = []
    with open(gui) as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            fileName = os.path.join(options.datadir, line + ".wav")
            sampleRate, data = wavfile.read(fileName)

            nSamples = len(data)

            # From miliseconds to samples
            ns_windowlength = int(round((options.windowlength * sampleRate) / 1000))
            ns_frameshift = int(round((options.frameshift * sampleRate) / 1000))
            ns_padding = int(round((options.padding * sampleRate) / 1000))

            frames = []
            for ini in range(-ns_padding, nSamples - ns_windowlength + ns_padding + 1, ns_frameshift):
                first_sample = max(0, ini)
                last_sample = min(nSamples, ini + ns_windowlength)
                frame = data[first_sample:last_sample]
                frames.append(frame)

            wavFiles.append({"fileName": fileName, "sampleRate": sampleRate, "frames": frames})
                

    return wavFiles



def main(options, args):
    """
    Main script function
    """
    # get the wav files
    wavFiles = getWavFiles(options, args[0])

    # print the algorithm name at the top of the directory
    header_file = os.path.join(os.path.dirname(wavFiles[0]["fileName"]), "algorithm.info")
    with open(header_file, 'wt') as header_file:
        print(options.method, file=header_file)


    for wavFile in wavFiles:
        f0_filename = wavFile["fileName"].replace(".wav", ".f0")
        with open(f0_filename, 'wt') as f0file:
            print("Processing:", wavFile["fileName"], "with", options.method, '->', f0_filename)
            for frame in wavFile["frames"]:
                # compute the pitch for each frame
                f0 = 0
                if options.method == "autocorrelation":
                    f0 = autocorr_method(frame, wavFile["sampleRate"])
                elif options.method == "amdf":
                    f0 = amdf_method(frame, wavFile["sampleRate"])
                elif options.method == "cepstrum":
                    f0 = cepstrum_method(frame, wavFile["sampleRate"])
                
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
        '-m', '--method', type='string', default='amdf',
        help='pitch detection method: autocorrelation, cepstrum or amdf (default)')

    options, args = optparser.parse_args()

    if options.method:
        if options.method not in ["autocorrelation", "cepstrum", "amdf"]:
            print("The method {} is not valid".format(options.method))
            optparser.print_help()
            exit(-1)

    if len(args) == 0:
        print("No FILELIST provided")
        optparser.print_help()
        exit(-1)

    main(options, args)
