#!/usr/bin/env python3

import os
import subprocess
import argparse
import compute_stft
from bids import BIDSLayout
import numpy as np
from util.io.iter_BIDSPaths import *
from util.io.bids import DataSink

def main(subs, skips):
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'

    layout = BIDSLayout(BIDS_ROOT, derivatives = True)
    fpaths = layout.get(scope = 'preprocessing',
                    suffix='epo',
                    extension = 'fif.gz',
                    return_type = 'filename')
    
    for (fpath, sub, task, run) in iter_BIDSPaths(fpaths):
        
        # if subs were given but sub is not in subs, don't preprocess
        if bool(subs) and sub not in subs:
            continue

        # if sub in skips, don't preprocess
        if sub in skips:
            continue

        # skip if subject is already decoded
        sink = DataSink(DERIV_ROOT, 'decoding')
        scores_fpath = sink.get_path(
            subject = sub,
            task = task,
            run = run,
            desc = 'predict_from_stft',
            suffix = 'scores',
            extension = 'npy',
        )
        if os.path.isfile(scores_fpath) and sub not in subs:
            print(f"Subject {sub} run {run} is already preprocessed")
            continue
        
        # Decode
        print('subprocess.check_call("sbatch ./predict_from_stft.py %s %s %s" % (fpath, sub, task, run, scores_fpath), shell=True)')
        subprocess.check_call("sbatch ./predict_from_stft.py %s %s %s %s %s" % (fpath, sub, task, run, scores_fpath), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run decode_from_stft.py over given subjects')
    parser.add_argument('--subs', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects to decode (e.g. 3 14 8), provide no argument to run over all subjects', 
                        default = [])
    parser.add_argument('--skips', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects NOT to decode (e.g. 1 9)', 
                        default = [])
    args = parser.parse_args()
    subs = args.subs
    skips = args.skips
    print(f"subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(subs, skips)
