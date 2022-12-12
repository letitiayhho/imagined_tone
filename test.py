from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychtoolbox import GetSecs, WaitSecs
import random


# --- Constants ---
FREQS = [190, 280]
TONE_DUR = 0.5
ISI = 0.5
TONES_PER_TRIAL = 4
N_TRIALS = 3

# --- Functions ---
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
    
    freqs = []
    marks = []
    
    for i in range(TONES_PER_TRIAL):
        mark = get_mark(index, sound = True)
        play_tone(WIN, MARKER, TONE_DUR, freq, mark)
        WaitSecs(ISI)
        
        freqs.append(freq)
        marks.append(mark)

    for i in range(TONES_PER_TRIAL):
        mark = get_mark(index, sound = False)
        display_cue_only(WIN, MARKER, TONE_DUR, mark)
        WaitSecs(ISI)
        
        freqs.append(freq)
        marks.append(mark)
        
    return(freq, freqs, marks)

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
        reward += 0.1
        feedback = visual.TextStim(WIN,
                  text = f"Spot on! You've now earned ${reward} for this block. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )
    elif response < freq:
        feedback = visual.TextStim(WIN,
                  text = f"You were {freq - response} Hz below the target. You've now earned ${reward} for this block. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )
    elif response > freq:
        feedback = visual.TextStim(WIN,
                  text = f"You were {response - freq} Hz above the target. You've now earned ${reward} for this block. Press 'enter' to continue.",
                  pos=(0.0, 0.0),
                  color=(1, 1, 1),
                  colorSpace='rgb'
                 )

    feedback.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    
    return(reward)

# KB = get_keyboard('Dell Dell USB Entry Keyboard')
# MARKER = EventMarker()
MARKER = None
WIN = get_window()
reward = 0

ready(WIN)

for trial in range(N_TRIALS):
    WaitSecs(0.5)
    fixation(WIN, 1)
    WaitSecs(0.5)
    freq, freqs, marks = get_trial(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
    white_noise(1)
    WaitSecs(0.5)
    displaced_freq = play_displaced_target(WIN, TONE_DUR, freq)
    response = pitch_adjustment(WIN, MARKER, TONE_DUR, displaced_freq)
    WaitSecs(0.5)
    reward = feedback(freq, response, reward)
    