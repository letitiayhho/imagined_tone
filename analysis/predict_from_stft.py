#!/usr/bin/env python3

#SBATCH --time=00:05:00
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=24G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/predict_from_stft_%j.log

import mne
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from mne.decoding import SlidingEstimator, cross_val_multiscore

from util.io.bids import DataSink

def main(fpath, sub, task, run, scores_fpath):
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'
    FIGS_ROOT = '../figs'

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
    print(f'y_imagined: {y_imagined}')
    
    print("---------- Load stft results ----------")
    sink = DataSink(DERIV_ROOT, 'decoding')
    
    # Load heard stfts
    stft_heard = sink.get_path(
        subject = sub,
        task = task,
        run = run,
        desc = 'stft',
        suffix = 'heard',
        extension = 'npy',
    )
    print(f'Loading stft from {stft_heard}')
    Zxxs_heard = np.load(stft_heard)

    # Reshape for decoder
    n_epochs_heard = np.shape(Zxxs_heard)[0]
    if n_epochs_heard != np.shape(events_heard)[0]:
        sys.exit('Incorrect number of epochs')
    n_freqs = 2
    n_chans = 62
    n_windows = 41
    Zxxs_heard = Zxxs_heard.reshape((n_epochs_heard, n_freqs*n_chans, n_windows)) # n_epochs, n_freqs*n_chans, n_windows

    # Load imagined stfts
    stft_imagined = sink.get_path(
        subject = sub,
        task = task,
        run = run,
        desc = 'stft',
        suffix = 'imagined',
        extension = 'npy',
    )
    print(f'Loading stft from {stft_imagined}')
    Zxxs_imagined = np.load(stft_imagined)

    # Reshape for decoder
    n_epochs_imagined = np.shape(Zxxs_imagined)[0]
    if n_epochs_imagined != np.shape(events_imagined)[0]:
        sys.exit('Incorrect number of epochs')
    n_freqs = 2
    n_chans = 62
    n_windows = 41
    Zxxs_imagined = Zxxs_imagined.reshape((n_epochs_imagined, n_freqs*n_chans, n_windows)) # n_epochs, n_freqs*n_chans, n_windows

    print("---------- Fit decoder ----------")
    n_stimuli = 2
    metric = 'accuracy'

    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(solver = 'liblinear')
    )

    print("Creating sliding estimators")
    time_decod = SlidingEstimator(clf)

    print("Fit estimators")
    estimator = time_decod.fit(Zxxs_heard, y_heard)

    print("---------- Apply decoder ----------")
    scores = estimator.score(Zxxs_imagined, y_imagined)

    print("---------- Save decoder scores ----------")
    print('Saving scores to: ' + scores_fpath)
    np.save(scores_fpath, scores)

    print("---------- Plot ----------")
    windows = list(range(len(scores)))
    msec_per_window = 1000/41
    x = [window*msec_per_window for window in windows]

    fig, ax = plt.subplots()
    ax.plot(x, scores, label = 'score')
    ax.axhline(1/n_stimuli, color = 'k', linestyle = '--', label = 'chance')
    ax.set_xlabel('Times')
    ax.set_ylabel(metric)  # Area Under the Curve
    ax.legend()
    ax.set_title('Sensor space decoding')

    # Save plot
    fig_fpath = FIGS_ROOT + '/subj-' + sub + '_' + 'task-imagine_' + 'run-' + run + '_decode_from_wavelets' + '.png'
    print('Saving figure to: ' + fig_fpath)
    plt.savefig(fig_fpath)

__doc__ = "Usage: ./decode_from_stft.py <sub> <task> <run>"

if __name__ == "__main__":
    print(len(sys.argv))
    print("Argument List:", str(sys.argv))
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit("Incorrect call to script")
    print("Reading args")
    FPATH = sys.argv[1]
    SUB = sys.argv[2]
    TASK = sys.argv[3]
    RUN = sys.argv[4]
    SCORES_FPATH = sys.argv[5]
    main(FPATH, SUB, TASK, RUN, SCORES_FPATH)
