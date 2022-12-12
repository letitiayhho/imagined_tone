from psychtoolbox import WaitSecs
from functions import *

# --- Constants ---
FREQS = [190, 280]
TONE_DUR = 0.5
ISI = 0.5
TONES_PER_TRIAL = 4
N_TRIALS = 3

# --- Task ---

SUB_NUM = input("Input subject number: ")
BLOCK_NUM = input("Input block number: ")

SEED = set_seed(SUB_NUM, BLOCK_NUM)
# KB = get_keyboard('Dell Dell USB Entry Keyboard')
# MARKER = EventMarker()
MARKER = None
WIN = get_window()

LOG = open_log(SUB_NUM, BLOCK_NUM)
reward = get_reward(LOG)
trial_num = get_trial_num(LOG)

ready(WIN)
while trial_num <= N_TRIALS:
    WaitSecs(0.5)
    fixation(WIN, 1)
    WaitSecs(0.5)
    freq, mark = get_trial(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
    white_noise(1)
    WaitSecs(0.5)
    displaced_freq = play_displaced_target(WIN, TONE_DUR, freq)
    response = pitch_adjustment(WIN, MARKER, TONE_DUR, displaced_freq)
    WaitSecs(0.5)
    correct, reward = feedback(freq, response, reward)
    print(displaced_freq)
    write_log(LOG, TONES_PER_TRIAL, SEED, SUB_NUM, BLOCK_NUM, trial_num, mark, freq, displaced_freq, response, correct, reward)
    trial_num += 1
    
    
