from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychtoolbox import GetSecs, WaitSecs
import numpy as np

FREQS = [180, 280]
TONE_DUR = 0.3
ISI = 0.3

# --- Setup the Window ---
WIN = visual.Window(
    size=[600, 300], fullscr=False, screen=0, 
    winType='pyglet', allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='height')
win.mouseVisible = True

# --- Play tones ---
def play_tone(TONE_DUR, ISI, freq):

    # Prepare sound and visuals
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    
    # Play sound and visuals
    prompt.draw()
    WIN.flip()
    snd.play()
    
    # Turn off visuals after tone is finished playing
    WaitSecs(TONE_DUR)
    WIN.flip()
    
    # Wait for ISI
    WaitSecs(ISI)
    return(freq)

# --- Prompt subject to imagine tones ---
def prompt_imagine_tone(WIN, TONE_DUR, ISI):
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()
    WaitSecs(ISI)

index = np.random.randint(0, len(FREQS))
freq = FREQS[index]
for i in range(3):
    play_tone(TONE_DUR, ISI, freq)
for i in range(3):
    prompt_imagine_tone(WIN, TONE_DUR, ISI)
    