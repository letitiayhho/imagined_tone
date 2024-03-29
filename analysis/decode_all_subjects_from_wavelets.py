#!/usr/bin/env python3

import os
import subprocess
import argparse
import compute_stft
from bids import BIDSLayout
import numpy as np
from util.io.iter_BIDSPaths import *
from util.io.bids import DataSink

def main(cond, force, subs, skips):
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
            desc = 'decode_from_wavelets',
            suffix = cond,
            extension = 'npy',
        )
        if os.path.isfile(scores_fpath) and force == False:
            print(f"Subject {sub} run {run} is already preprocessed")
            continue
        
        # Decode
        print(f'subprocess.check_call("sbatch ./decode_from_wavelets.py %s %s %s %s %s %s" % ({fpath}, {sub}, {task}, {run}, {cond}, {scores_fpath}), shell=True)')
        subprocess.check_call("sbatch ./decode_from_wavelets.py %s %s %s %s %s %s" % (fpath, sub, task, run, cond, scores_fpath), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run decode_from_wavelets.py over given subjects')
    parser.add_argument('cond',
                        type = str,
                        nargs = 1,
                        help = 'condition: imagined or heard',
                        choices = ['heard', 'imagined'])
    parser.add_argument('--force',
                        type = bool,
                        nargs = 1,
                        default = False,
                        help = 'If true run decode_from_wavelets.py even if save_fpath file already exists')
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
    cond = args.cond[0]
    force = args.force
    subs = args.subs
    skips = args.skips
    print(f"cond : {cond}, force : {force}, subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(cond, force, subs, skips)
