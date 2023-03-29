#!/usr/bin/env python3

#SBATCH --time=00:10:00 
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem-per-cpu=16G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/decode_from_wavelets_%j.log

import gc
import sys
import mne
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from typing import Tuple, Iterator
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree
from mne.time_frequency import tfr_morlet
from bids import BIDSLayout

from sklearn.pipeline import make_pipeline
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from mne.decoding import SlidingEstimator, cross_val_multiscore

def main(fpath, sub, task, run, scores_fpath):
    BIDS_ROOT = '../data/bids'
    FIGS_ROOT = '../figs'
    STIM_FREQS = np.array([50, 100, 150, 200, 250])

    np.random.seed(0)

    print("---------- Load data ----------")
    print(fpath)
    epochs = mne.read_epochs(fpath)
    
    print("---------- Separate into heard and imagined epochs objects ----------")
    epochs_heard = epochs['11', '12']
    events_heard = epochs_heard.events
    epochs_imagined = epochs['21', '22']
    events_imagined = epochs_imagined.events
    
    print("---------- Create event label dicts ----------")
    print(epochs_heard.event_id)
    label_dict_heard = {10001 : 0, 10002 : 1}
    print(epochs_imagined.event_id)
    label_dict_imagined = {10003 : 0, 10004 : 1}

    print("---------- Create target array ----------")
    labels_heard = pd.Series(events_heard[:, 2])
    y_heard = labels_heard.replace(label_dict_heard)
    le = preprocessing.LabelEncoder()
    y_heard = le.fit_transform(y_heard)
    print(f'y_heard: {y_heard}')

    labels_imagined = pd.Series(events_imagined[:, 2])
    y_imagined = labels_imagined.replace(label_dict_imagined)
    le = preprocessing.LabelEncoder()
    y_imagined = le.fit_transform(y_imagined)
    print(f'y_heard: {y_imagined}')
    
    print("---------- Compute power ----------")
    n_cycles = STIM_FREQS / 7 # different number of cycle per frequency
                               # higher constant, fewer windows, maybe?

    # For epochs heard
    power_heard = tfr_morlet(epochs_heard,
                       freqs = STIM_FREQS,
                       n_cycles = n_cycles,
                       use_fft = True,
                       return_itc = False,
                       decim = 3,
                       n_jobs = 1,
                       average = False)
    power_heard = np.log10(power_heard)

    # Get some information
    n_epochs = np.shape(power_heard)[0]
    n_channels = np.shape(power_heard)[1]
    n_freqs = np.shape(power_heard)[2]
    n_windows = np.shape(power_heard)[3]
    print("n_windows: " + str(n_windows))

    # Reshape for classifier
    X_heard = power_heard.reshape((n_epochs, n_freqs * n_channels, n_windows)) # Set order to preserve epoch order
    print(np.shape(X_heard))

    # Repeat for epochs_imagined
    power_imagined = tfr_morlet(epochs_imagined,
                       freqs = STIM_FREQS,
                       n_cycles = n_cycles,
                       use_fft = True,
                       return_itc = False,
                       decim = 3,
                       n_jobs = 1,
                       average = False)
    power_imagined = np.log10(power_imagined)

    # Get some information
    n_epochs = np.shape(power_imagined)[0]
    n_channels = np.shape(power_imagined)[1]
    n_freqs = np.shape(power_imagined)[2]
    n_windows = np.shape(power_imagined)[3]
    print("n_windows: " + str(n_windows))

    # Reshape for classifier
    X_imagined = power_imagined.reshape((n_epochs, n_freqs * n_channels, n_windows)) # Set order to preserve epoch order
    print(np.shape(X_imagined))
    
    del epochs_heard
    del epochs_imagined
    gc.collect()

    print("---------- Decode ----------")
    n_stimuli = 2
    metric = 'accuracy'

    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(solver = 'liblinear')
    )

    print("Creating sliding estimators")
    time_decod = SlidingEstimator(clf)

    print("Fit estimators")
    estimator = time_decod.fit(X_heard, y_heard)
    
    print("---------- Apply decoder ----------")
    scores = estimator.score(X_imagined, y_imagined)

    # Save decoder score_shape
    print("---------- Save decoder scores ----------")
    print('Saving scores to: ' + scores_fpath)
    np.save(scores_fpath, scores)

    # Plot
    print("---------- Plot ----------")
    windows = list(range(len(scores)))
    msec_per_window = 1000/1667
    x = [window*msec_per_window for window in windows]
    
    fig, ax = plt.subplots()
    ax.plot(x, scores, label = 'score')
    ax.axhline(1/n_stimuli, color = 'k', linestyle = '--', label = 'chance')
    ax.set_xlabel('msec')
    ax.set_ylabel(metric)  # Area Under the Curve
    ax.legend()
    ax.set_title('Sensor space decoding')

    # Save plot
    fig_fpath = FIGS_ROOT + '/subj-' + sub + '_' + 'task-imagine_' + 'run-' + run + '_predict_from_wavelets' + '.png'
    print('Saving figure to: ' + fig_fpath)
    plt.savefig(fig_fpath)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit(1)
    fpath = sys.argv[1]
    sub = sys.argv[2]
    task = sys.argv[3]
    run = sys.argv[4]
    scores_fpath = sys.argv[5]
    main(fpath, sub, task, run, scores_fpath)
