from functions import *
FREQS = [190, 280]
TONE_DUR = 0.4
ISI = 0.4
N_TONES = 1000

# MARKER = EventMarker()
MARKER = None

freq = FREQS[random.randint(0, 1)]
for i in range(1000):
    mark = get_mark(index, sound = True)
    snd = Sound(freq, secs = TONE_DUR)
    snd.play(when = now + 0.001)
    WaitSecs(0.001)
    MARKER.send(mark)
    WaitSecs(TONE_DUR)
    WaitSecs(ISI)
