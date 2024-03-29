from psychtoolbox import WaitSecs
from functions import *
from events import EventMarker

# --- Constants ---
FREQS = [190, 280]
TONE_DUR = 0.5
ISI = 1.2
TONES_PER_TRIAL = 5

# --- Task ---

SUB_NUM = input('Input subject number: ')
BLOCK_NUM = input('Input block number [0-5]: ')

set_cwd()
KB = get_keyboard('Dell Dell USB Entry Keyboard')
MARKER = EventMarker()
WIN = get_window()

LOG = open_log(SUB_NUM, BLOCK_NUM)
reward = get_reward(LOG)
trial_num = get_trial_num(LOG)
n_trials = get_n_trials(BLOCK_NUM)

start(WIN, BLOCK_NUM, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
ready(WIN)
while trial_num <= n_trials:
    print(f'trial_num: {trial_num}')
    seed = set_seed(SUB_NUM, BLOCK_NUM, trial_num)
    WaitSecs(0.5)
    fixation(WIN, 1)
    WaitSecs(0.5)
    freq, mark = get_trial(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
    white_noise(1)
    WaitSecs(0.5)
    displaced_freq = play_displaced_target(WIN, MARKER, TONE_DUR, freq)
    response = pitch_adjustment(WIN, TONE_DUR, displaced_freq)
    WaitSecs(0.5)
    diff, reward = feedback(WIN, freq, response, reward)
    print(displaced_freq)
    write_log(LOG, TONES_PER_TRIAL, seed, SUB_NUM, BLOCK_NUM, trial_num, mark, freq, ISI, displaced_freq, response, diff, reward)
    trial_num += 1
    
 
end(WIN, BLOCK_NUM, reward)

print("Block over :-)")
core.quit()
