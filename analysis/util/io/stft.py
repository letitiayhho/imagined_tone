import numpy as np
import mne
import pandas as pd
from scipy import signal
from scipy import signal
from util.io.bids import DataSink

def summarize_stft(f, Zxx, n_epochs, condition_freqs): # approximate power at the condition freqs
    Zxx_condensed = np.empty([n_epochs, len(condition_freqs), 41])
    
    for i in range(len(condition_freqs)):
        
        # find indexes of freqs surrounding the condition freq
        freq = condition_freqs[i]
        a = int(np.argwhere(f < freq)[-1])
        b = a+1
        
        # subset power for the condition freq
        condition_Zxx = Zxx[:,a:b+1, :]
        
        # take average to get approximate for power at condition freq
        condition_Zxx = np.mean(condition_Zxx, axis = 1)
        Zxx_condensed[:, i, :] = condition_Zxx
    
    return Zxx_condensed

def get_stft_for_one_channel(x, fs, n_epochs, condition_freqs): # where x is n_epochs, n_windows
    f, t, Zxx = signal.stft(x, fs) 

    # Take real values
    Zxx = np.abs(Zxx)
    
    # Summarize to frequencies of interest
    Zxx = summarize_stft(f, Zxx, n_epochs, condition_freqs)
    
    return (f, t, Zxx)
