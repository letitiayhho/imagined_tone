import random
from functions import *
from events import EventMarker

FREQS = [190, 280]
TONE_DUR = 0.4
ISI = 0.4
N_TONES = 1000

MARKER = EventMarker()
# MARKER = None

index = random.randint(0,1)
freq = FREQS[index]
for i in range(1000):
    print(i)
    mark = get_mark(index, sound = True)
    snd = Sound(freq, secs = TONE_DUR)
    snd.play()
    WaitSecs(0.001)
    MARKER.send(mark)
    WaitSecs(TONE_DUR)
    WaitSecs(ISI)
