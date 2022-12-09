from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychtoolbox import GetSecs, WaitSecs
import numpy as np


# --- Constants ---
FREQS = [180, 280]
TONE_DUR = 0.5
ISI = 0.5
TONES_PER_TRIAL = 4

# --- Functions ---
def get_window():
    WIN = visual.Window(size = (300, 200),
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

def fixation(WIN, secs):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    WaitSecs(secs)
    WIN.flip()
    return(fixation)

def play_tone(TONE_DUR, ISI, freq, mark):

    # Prepare sound and visuals
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    
    # Play sound
    now = GetSecs()
    snd.play(when = now + 0.001)

    # Send marker and update display when tone starts to play
    WaitSecs(0.001)
#     MARKER.send(mark)
    WIN.flip()
    
    # Turn off visuals after tone is finished playing
    WaitSecs(TONE_DUR)
    WIN.flip()
    
    # Wait for ISI
    WaitSecs(ISI)

def prompt_imagine_tone(WIN, TONE_DUR, ISI, mark):

    # Prepare visuals
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    now = GetSecs()

    # Prompt subject to imagine tone
    WaitSecs(0.001)
#     MARKER.send(mark)
    WIN.flip()
    
    # Turn off visuals 
    WaitSecs(TONE_DUR)
    WIN.flip()
    
    # Wait for ISI
    WaitSecs(ISI)
    
def get_mark(index, heard):
    if heard: # if tone was heard, marker starts with '1'
        mark = int(str(1) + str(index + 1))
    else: # if tone was imagined, marker starts with '2'
        mark = int(str(2) + str(index + 1))
    return(mark)

def get_trial(FREQS, TONE_DUR, ISI, WIN, TONES_PER_TRIAL):
    index = np.random.randint(0, len(FREQS))
    freq = FREQS[index]
    
    freqs = []
    marks = []
    
    for i in range(TONES_PER_TRIAL):
        mark = get_mark(index, heard = True)
        play_tone(TONE_DUR, ISI, freq, mark)
        
        freqs.append(freq)
        marks.append(mark)

    for i in range(TONES_PER_TRIAL):
        mark = get_mark(index, heard = False)
        prompt_imagine_tone(WIN, TONE_DUR, ISI, mark)
        
        freqs.append(freq)
        marks.append(mark)
        
    return(freq, freqs, marks)

def white_noise(secs):
    # jitter
    # play white noise for jittered duration
    
def play_displaced_target(WIN, TONE_DUR, freq):
    # Prepare sound
    displacement = np.random.randint(-10, 10)
    displaced_freq = freq + displacement
    play_sound_with_cue(WIN, TONE_DUR, displaced_freq)
#     snd = Sound(displaced_freq, secs = TONE_DUR)
    
#     # Prepare visuals
#     prompt = visual.TextStim(WIN, '*')
#     prompt.draw()
    
#     # Play sound
#     now = GetSecs()
#     snd.play(when = now + 0.001)
#     WaitSecs(0.001)
#     WIN.flip()
    
    return(displayed_freq)
    
def pitch_adjustment(WIN, TONE_DUR, displaced_freq):

    # Fetch response
    keylist = ['up', 'down', 'return']

    while True:
        keys = event.getKeys(keyList = keylist)
        if 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'up' in keys:
                displaced_freq += 1
                play_sound_with_cue(WIN, TONE_DUR, displaced_freq)
            elif 'down' in keys:
                displaced_freq -= 1
                play_sound_with_cue(WIN, TONE_DUR, displaced_freq)

    response = displaced_freq
    return(response)


def play_sound_with_cue(WIN, TONE_DUR, freq):
    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.Play(when = now + 0.001)
    WaitSecs(0.001)
    WIN.flip()

def feedback(freq, response):
    # display feedback


WIN = get_window()
# KB = get_keyboard('Dell Dell USB Entry Keyboard')

for i in range(3):
    WaitSecs(1)
    fixation(WIN, 2)
    WaitSecs(1)
    freq, freqs, marks = get_trial(FREQS, TONE_DUR, ISI, WIN)
    WaitSecs(1)
    white_noise(1)
    WaitSecs(1)
    displaced_freq = play_displaced_target(WIN, TONE_DUR, freq)
    response = pitch_adjustment(displaced_freq)
    WaitSecs(1)
    feedback(freq, response)
    WaitSecs(1)
    