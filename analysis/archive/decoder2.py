#!/usr/bin/env python

#SBATCH --time=00:20:00
#SBATCH --partition=broadwl
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=16gb
#SBATCH --ntasks-per-node=5
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/decoding_%j.log

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

from util.io.bids import DataSink
from util.io.iter_fpaths import iter_fpaths

# for (fpath, sub, task, run) in iter_fpaths(BIDS_ROOT):
def main() -> None:
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'
    FIGS_ROOT = '../figs'
    STIM_FREQS = np.array([50, 100, 150, 200, 250])
    FS = 2000

    for (fpath, sub, task, run) in iter_fpaths(BIDS_ROOT):

        np.random.seed(0)

        print("---------- Load data ----------")
        epochs = mne.read_epochs(fpath)
        epochs = epochs.crop(tmin = 0)
        events = mne.read_events(fpath)

        # Compute power
        print("---------- Compute power ----------")
        n_cycles = STIM_FREQS / 7.  # different number of cycle per frequency
        power = tfr_morlet(epochs,
                           freqs = STIM_FREQS,
                           n_cycles = n_cycles,
                           use_fft = True,
                           return_itc = False,
                           decim = 3,
                           n_jobs = 1,
                           average = False)
        power = np.log10(power)

        # Get some information
        n_epochs = np.shape(power)[0]
        n_channels = np.shape(power)[1]
        n_freqs = np.shape(power)[2]
        n_windows = np.shape(power)[3]

        # Reshape for classifier
        X = power.reshape((n_epochs, n_freqs * n_channels, n_windows)) # Set order to preserve epoch order

        # Create array of condition labels
        print("---------- Create target array ----------")
        labels = pd.Series(events[:, 2])
        y = labels.replace({10001 : 0, 10002 : 1, 10003 : 2, 10004 : 3, 10005 : 4})
        le = preprocessing.LabelEncoder()
        y = le.fit_transform(y)

        # Decode
        print("---------- Decode ----------")
        n_stimuli = 5
        metric = 'accuracy'

        clf = make_pipeline(
            StandardScaler(),
            LogisticRegression(solver = 'liblinear')
        )

        print("Creating sliding estimators")
        time_decod = SlidingEstimator(clf)

        print("Fit estimators")
        scores = cross_val_multiscore(
            time_decod,
            X, # a trials x features x time array
            y, # an (n_trials,) array of integer condition labels
            cv = 5, # use stratified 5-fold cross-validation
        #     scoring = 'balanced_accuracy',
            n_jobs = -1, # use all available CPU cores
        #     verbose = 3,
        )
        scores = np.mean(scores, axis = 0) # average across cv splits

        # Save decoder score_shape
        print("---------- Save decoder scores ----------")
        sink = DataSink(DERIV_ROOT, 'decoding')
        scores_fpath = sink.get_path(
            subject = sub,
            task = task,
            run = run,
    	    desc = 'log_reg',
            suffix = 'scores',
            extension = 'npy',
        )
        print('Saving scores to: ' + scores_fpath)
        np.save(scores_fpath, scores)

        # Plot
        print("---------- Plot ----------")
        fig, ax = plt.subplots()
        ax.plot(range(len(scores)), scores, label = 'score')
        ax.axhline(1/n_stimuli, color = 'k', linestyle = '--', label = 'chance')
        ax.set_xlabel('Times')
        ax.set_ylabel(metric)  # Area Under the Curve
        ax.legend()
        ax.set_title('Sensor space decoding')

        # Save plot
        fig_fpath = FIGS_ROOT + '/subj-' + sub + '_' + 'task-pitch_' + 'run-' + run + '.png'
        print('Saving figure to: ' + fig_fpath)
        plt.savefig(fig_fpath)

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(__doc__)
        sys.exit(1)
    main()
