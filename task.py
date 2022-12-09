from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychtoolbox import GetSecs, WaitSecs
#from events import EventMarker
import numpy as np
import os.path
import csv

# --- Setup the Window ---
win = visual.Window(
    size=[200, 100], fullscr=False, screen=0, 
    winType='pyglet', allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='height')
win.mouseVisible = True

# --- Setup keyboard ---
from psychopy.hardware import keyboard
from psychopy import core

kb = keyboard.Keyboard()

# during your trial
kb.clock.reset()  # when you want to start the timer from
keys = kb.getKeys(['space', 'escape'], waitRelease=True)
if 'escape' in keys:
    core.quit()
for key in keys:
    print(key.name, key.rt, key.duration)

TEST_MODE = False
TRIALS = 10 # takes about 6:40 per block
FREQS = [50, 100, 150, 200, 250]

#sub_num = input("Input subject number: ")
#block_num = input("Input block number: ")
sub_num = "0"
block_num = "0"

# set subject number and block as seed
seed = int(sub_num + "0" + block_num)
print("Current seed: " + str(seed))
np.random.seed(seed)

# count trial progress in log file
log = "..\data\logs\subj_" + sub_num + "_block_" + block_num + ".log"
if not os.path.isfile(log): # create log file if it doesn't exist
    with open(log, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['trial', 'freq', 'marker'])
trial_count = sum(1 for line in open(log))
print("Current trial number: " + str(trial_count))

# --- Initialize components for Routine "WelcomeScreen" ---
WelcomeScreenroutine = visual.TextStim(win=win, name='WelcomeScreenroutine',
    text='Welcome. This is an auditory perception study.',
    font='Arial',
    pos=(-0.3, 0.25), height=0.04, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
welcome_key_resp = keyboard.Keyboard()
welcome_key_resp.keys = ['space']

# --- Initialize components for Routine "Instructions" ---
text_instr = visual.TextStim(win=win, name='text_instr',
    text='First, you will hear a tone. Pay attention carefully as you will be asked to imagine the tone after it has been played. ',
    font='Arial',
    pos=(-0.3, 0.25), height=0.04, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
instruction_key_resp = keyboard.Keyboard()
instruction_key_resp.keys = ['space']

# --- Initialize components for Routine "Instructions2" ---
text_instr_2 = visual.TextStim(win=win, name='text_instr_2',
    text='After hearing the tone, a brief pause will ensue. After this pause, a signifier will be presented on the screen and you will be expected to imagine the tone you just heard. ',
    font='Arial',
    pos=(-0.3, 0.25), height=0.04, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
instructions2_key_resp = keyboard.Keyboard()
instructions2_key_resp.keys = ['space']

# start the experiment
WaitSecs(5.)

for i in range(trial_count, TRIALS + 1):
    print(i)

    if TEST_MODE:
        freq = 100
    else:
        index = np.random.randint(0, len(FREQS))
        freq = FREQS[index]
        mark = index + 1
    snd = Sound(freq, secs = 0.2)

    # schedule sound
    now = GetSecs()
    snd.play(when = now + 0.1)
    WaitSecs(0.1)
    #marker.send(mark)

    # log trial info
    with open(log, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([i, freq, mark])

    # add jitter between TRIALS
    WaitSecs(0.2+np.random.uniform(0, 0.1))
    
#INSERT BLANK SCREEN#

#INSERT SCREEN WITH SIGNIFIER FOR IMAGINED SEQUENCE#
    
# --- Initialize components for Routine "Instructions3" ---
text_instr_3 = visual.TextStim(win=win, name='text_instr_3',
    text='Now you will hear a random tone. After hearing this tone, please indicate if this tone is the tone you heard at the beginning of the experiment. ',
    font='Arial',
    pos=(-0.3, 0.25), height=0.04, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
instructions3_key_resp = keyboard.Keyboard()
instructions3_key_resp.keys = ['space']

# random tone after imagined sequence
WaitSecs(5.)

for i in range(trial_count, TRIALS + 1):
    print(i)

    if TEST_MODE:
        freq = 100
    else:
        index = np.random.randint(0, len(FREQS))
        freq = FREQS[index]
        mark = index + 1
    snd = Sound(freq, secs = 0.2)

    # schedule sound
    now = GetSecs()
    snd.play(when = now + 0.1)
    WaitSecs(0.1)
    #marker.send(mark)

    # log trial info
    with open(log, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([i, freq, mark])

    # add jitter between TRIALS
    WaitSecs(0.2+np.random.uniform(0, 0.1))

# --- Initialize components for Routine "Instructions4" ---
text_instr_4 = visual.TextStim(win=win, name='text_instr_4',
    text='Is this the tone you heard at the beginning of the experiment? ',
    font='Arial',
    pos=(-0.3, 0.25), height=0.04, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
instructions4_key_resp = keyboard.Keyboard()
instructions4_key_resp.keys = ['space']

# --- Initialize components for Routine "Instructions5" ---
text_instr_5 = visual.TextStim(win=win, name='text_instr_5',
    text='Thank you for participating in this study. ',
    font='Arial',
    pos=(-0.3, 0.25), height=0.04, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
instructions5_key_resp = keyboard.Keyboard()
instructions5_key_resp.keys = ['space']

#marker.close()
print("Done.")
