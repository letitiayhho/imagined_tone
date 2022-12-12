from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychtoolbox import GetSecs, WaitSecs
import random
import os
import pandas as pd

# --- Constants ---
FREQS = [190, 280]
TONE_DUR = 0.5
ISI = 0.5
TONES_PER_TRIAL = 4
N_TRIALS = 3

# --- Functions ---
def set_seed(SUB_NUM, BLOCK_NUM):
    SEED = int(SUB_NUM + "0" + BLOCK_NUM)
    print("Current seed: " + str(SEED))
    random.seed(SEED)

def get_window():
    WIN = visual.Window(size = (800, 500),
    screen = -1,
    units = "norm",
    fullscr = False,
    pos = (0, 0),
    allowGUI = False)
    return(WIN)

def get_keyboard(dev_name):
    devs = hid.get_keyboard_indices()
    idxs = devs[0]
    names = devs[1]
    try:
        idx = [idxs[i] for i, nm in enumerate(names) if nm == dev_name][0]
    except:
        raise Exception(
        'Cannot find %s! Available devices are %s.'%(dev_name, ', '.join(names))
        )
    return Keyboard(idx)

def open_log(SUB_NUM, BLOCK_NUM):
    log = "data/logs/sub-" + SUB_NUM + "_blk-" + BLOCK_NUM + ".log"

    if not os.path.isfile(log): # create log file if it doesn't exist
        print(f"Creating {log}")
        d = {
            'seed': [],
            'sub_num': [],
            'block_num': [],
            'trial_num': [],
            'tone_num': [],
            'heard': [],
            'mark': [],
            'freq': [],
            'displaced_freq': [],
            'response': [],
            'correct': [],
            'reward': [],
            }
        print(d)
        df = pd.DataFrame(data = d)
        df.to_csv(log, mode='w', index = False)
    return(log)

def get_reward(LOG):
    log = pd.read_csv(LOG)
    rewards = log['reward']
    if len(rewards) == 0:
        reward = 0
    else:
        reward = rewards.iloc[-1]
    reward = int(reward)
    return(reward)

def get_trial_num(LOG):
    log = pd.read_csv(LOG)
    trial_nums = log['trial_num']
    if len(trial_nums) == 0:
        trial_num = 1
    else:
        trial_num = trial_nums.iloc[-1] + 1
    trial_num = int(trial_num)
    return(trial_num)

def ready(WIN):
    block_begin = visual.TextStim(WIN,
                                  text = "Press 'enter' to begin!",
                                  pos=(0.0, 0.0),
                                  color=(1, 1, 1),
                                  colorSpace='rgb')
    block_begin.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()

def fixation(WIN, secs):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    jitter = random.uniform(-0.1, 0.1)
    WaitSecs(secs + jitter)
    WIN.flip()
    return(fixation)

def play_tone(WIN, MARKER, TONE_DUR, freq, mark = False):
    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.play(when = now + 0.001)
    WaitSecs(0.001)
#     MARKER.send(mark) if isinstance(mark, int) else None
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()
    
def display_cue_only(WIN, MARKER, TONE_DUR, mark):
    now = GetSecs()
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    WaitSecs(0.001)
#     MARKER.send(mark)
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()
    
def get_mark(index, sound):
    if sound: # if tone was played, marker starts with '1'
        mark = int(str(1) + str(index + 1))
    else: # if tone was imagined, marker starts with '2'
        mark = int(str(2) + str(index + 1))
    return(mark)

def get_trial(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL):
    index = random.randint(0, 1)
    freq = FREQS[index]
    
    mark_list = []
    for i in range(TONES_PER_TRIAL):
        mark = get_mark(index, sound = True)
        play_tone(WIN, MARKER, TONE_DUR, freq, mark)
        WaitSecs(ISI)        
        mark_list.append(mark)

    for i in range(TONES_PER_TRIAL):
        mark = get_mark(index, sound = False)
        display_cue_only(WIN, MARKER, TONE_DUR, mark)
        WaitSecs(ISI)
        mark_list.append(mark)
            
    return(freq, mark_list)

def white_noise(secs):
    start = random.uniform(0, 8)
    stop = start + secs + random.uniform(-0.1, 0.1)
    snd = Sound('gaussianwhitenoise.wav', startTime = start, stopTime = stop, volume = 0.5)
    snd.play()
    WaitSecs(stop - start)
    
def play_displaced_target(WIN, TONE_DUR, freq):
    displacement = random.randint(-10, 10)
    displaced_freq = freq + displacement
    play_tone(WIN, MARKER, TONE_DUR, displaced_freq)
    return(displaced_freq)
    
def pitch_adjustment(WIN, MARKER, TONE_DUR, displaced_freq):
    keylist = ['up', 'down', 'return']

    while True:
        keys = event.getKeys(keyList = keylist)
        if 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'up' in keys:
                displaced_freq += 1
                play_tone(WIN, MARKER, TONE_DUR, displaced_freq)
            elif 'down' in keys:
                displaced_freq -= 1
                play_tone(WIN, MARKER, TONE_DUR, displaced_freq)

    response = displaced_freq
    return(response)

def feedback(freq, response, reward):
    
    if freq == response:
        correct = 1
        reward += 0.1
        feedback = visual.TextStim(WIN,
                  text = f"Spot on! You earned ${reward} for this block. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )
    elif response < freq:
        correct = 0
        feedback = visual.TextStim(WIN,
                  text = f"You were {freq - response} Hz below the target. You earned ${reward} for this block. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )
    elif response > freq:
        correct = 0
        feedback = visual.TextStim(WIN,
                  text = f"You were {response - freq} Hz above the target. You earned ${reward} for this block. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )

    feedback.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    
    return(correct, reward)

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, TONES_PER_TRIAL, SEED, SUB_NUM, BLOCK_NUM, trial_num, mark, freq, displaced_freq, response, correct, reward):
    print("Writing to log file")
    d = {
        'seed': broadcast(TONES_PER_TRIAL * 2, SEED),
        'sub_num': broadcast(TONES_PER_TRIAL * 2, SUB_NUM),
        'block_num': broadcast(TONES_PER_TRIAL * 2, BLOCK_NUM),
        'trial_num': broadcast(TONES_PER_TRIAL * 2, trial_num),
        'tone_num' : list(range(1, TONES_PER_TRIAL * 2 + 1 )),
        'heard' : [True]*TONES_PER_TRIAL + [False] * TONES_PER_TRIAL,
        'mark': mark,
        'freq': broadcast(TONES_PER_TRIAL * 2, freq),
        'displaced_freq': broadcast(TONES_PER_TRIAL * 2, displaced_freq),
        'response': broadcast(TONES_PER_TRIAL * 2, response),
        'correct': broadcast(TONES_PER_TRIAL * 2, correct),
        'reward': broadcast(TONES_PER_TRIAL * 2, reward),
        }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)

    
    
    
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
while trial_num < N_TRIALS:
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
    
    
