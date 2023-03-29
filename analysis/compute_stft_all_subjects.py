#!/usr/bin/env python3

import os
import subprocess
import argparse
from bids import BIDSLayout
from util.io.bids import DataSink
from util.io.iter_BIDSPaths import *

def main(cond, force, subs, skips) -> None:
    BIDS_ROOT = '../data/bids'
    layout = BIDSLayout(BIDS_ROOT, derivatives = True)
    fpaths = layout.get(scope = 'preprocessing',
                    suffix='epo',
                    extension = 'fif.gz',
                    return_type = 'filename')

    for (fpath, sub, task, run) in iter_BIDSPaths(fpaths):
        # Don't run if file already exists
        DERIV_ROOT = '../data/bids/derivatives'
        sink = DataSink(DERIV_ROOT, 'decoding')
        save_fpath = sink.get_path(
            subject = sub,
            task = task,
            run = run,
            desc = 'stft',
            suffix = cond,
            extension = 'npy',
        )
        if os.path.isfile(save_fpath) and force == False:
            print(f"Stft already computed for {sub} run {run} cond {cond}")
            continue
        
        # if subs were given but sub is not in subs, don't preprocess
        if bool(subs) and sub not in subs:
            continue

        # if sub in skips, don't preprocess
        if sub in skips:
            continue

        # Get stft
        print(f'subprocess.check_call("sbatch ./compute_stft.py %s %s %s %s %s %s" % ({fpath}, {sub}, {task}, {run}, {cond}, {save_fpath}), shell=True)')
        subprocess.check_call("sbatch ./compute_stft.py %s %s %s %s %s %s" % (fpath, sub, task, run, cond, save_fpath), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run compute_stft.py over given subjects')
    parser.add_argument('cond',
                        type = str,
                        nargs = 1,
                        help = 'condition: heard/imagined',
                        choices = ['heard', 'imagined'])
    parser.add_argument('--force',
                        type = bool,
                        nargs = 1,
                        default = False,
                        help = 'If true run compute_stft.py even if save_fpath file already exists')
    parser.add_argument('--subs', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects to compute stft for (e.g. 3 14 8), provide no argument to run over all subjects', 
                        default = [])
    parser.add_argument('--skips', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects NOT to stft for (e.g. 1 9)', 
                        default = [])
    args = parser.parse_args()
    cond = args.cond[0]
    force = args.force
    subs = args.subs
    skips = args.skips
    print(f"force : {force}, subs: {subs}, skips : {skips}, cond : {cond}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(cond, force, subs, skips)
