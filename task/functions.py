from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
from psychopy.sound.backend_ptb import SoundPTB as Sound
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychtoolbox import GetSecs, WaitSecs, hid
from psychopy.hardware.keyboard import Keyboard
import random
#import time
import os
import git
import pandas as pd

def set_cwd(): # set working directory to git top level
    repo = git.Repo('.', search_parent_directories=True)
    os.chdir(repo.working_tree_dir)
    print(repo.working_tree_dir)

def get_window():
    WIN = visual.Window(size = (1920, 1080),
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
            'diff': [],
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
    reward = float(reward)
    print(f'reward: {reward}')
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

def get_n_trials(BLOCK_NUM):
    if BLOCK_NUM == "0":
        n_trials = 3
    else:
        n_trials = 30
    return(n_trials)

def start(WIN, BLOCK_NUM, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL):
    if BLOCK_NUM == "0":
        instructions(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
    else:
        block_welcome(WIN, BLOCK_NUM)

def display_instructions(WIN, text):
    instructions = visual.TextStim(WIN, text = text)
    instructions.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()
    print(text)

def instructions(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL):
    display_instructions(WIN, "Welcome to the experiment. \n \n  Press 'enter' to begin.")
    display_instructions(WIN, "We are interested in how your brain represents imagined tones. In each trial the '*' symbol will appear five times at a constant rhythm. A tone will be played at the same time as the first four '*'. At the fifth '*' the target tone will NOT play. \n \n Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "When the '*' symbol appears without the target tone, try to imagine the sound of the target tone as accurately as you can. Try to imagine the tone as if you were actually listening to the tone! Try your best to do this without humming. It will help not to breathe out of your nose or mouth when imagining the tone. \n \n Press 'enter' for an example.")
    
    freq, mark_list = get_trial(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
    
    display_instructions(WIN, "At the end of each tone sequence, you will hear a short burst of white noise as a distractor, followed by a pitch-adjusted version of the target tone. Please use the 'up' and 'down' arrow keys to adjust the pitch of the displaced tone until it matches the target tone then press 'enter' to submit your answer. \n \n  Press 'enter' for an example.")
    
    freq, mark = get_trial(WIN, MARKER, FREQS, TONE_DUR, ISI, TONES_PER_TRIAL)
    white_noise(1)
    WaitSecs(0.5)
    displaced_freq = play_displaced_target(WIN, MARKER, TONE_DUR, freq)
    response = pitch_adjustment(WIN, TONE_DUR, displaced_freq)

    display_instructions(WIN, "You will receive an extra $0.50 every time you correctly identify the pitch of the original target tone, and $0.25 if you come close enough. You may earn up to $10 for this task. \n \n  Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "Lastly, as this is an EEG experiment it is important for you not to move your body, move your your eyes, or blink while the tones are playing. To help with this, keep your gaze on the '*'s and stay relaxed while they are on the screen. \n \n  Press 'enter' for the remaining instructions.")
    display_instructions(WIN, "You will now complete three practice trials. Please let you experimenter know if you have any questions or are experiencing any difficulties with the display or audio. \n \n Press 'enter' to continue to the practice trials.")

def block_welcome(WIN, BLOCK_NUM):
    display_instructions(WIN, f"Welcome to block number {BLOCK_NUM}/5. \n \n Press 'enter' to continue.")
    display_instructions(WIN, "Remember that when the tones are playing, keep your gaze on the '*' cues, try not to blink, and stay relaxed. Remember not to subvocalize or breathe out of your nose or mouth when you imagine the tones. \n \n Press 'enter' to begin the block!")

def ready(WIN):
    block_begin = visual.TextStim(WIN, text = "Press 'enter' to begin!")
    block_begin.draw()
    WIN.flip()
    event.waitKeys(keyList = ['return'])
    WIN.flip()

def set_seed(SUB_NUM, BLOCK_NUM, trial_num):
    seed = int(SUB_NUM + "0" + BLOCK_NUM + "0" + str(trial_num))
    print("Current seed: " + str(seed))
    random.seed(seed)
    return(seed)

def fixation(WIN, secs):
    fixation = visual.TextStim(WIN, '+')
    fixation.draw()
    WIN.flip()
    jitter = random.uniform(-0.1, 0.1)
    WaitSecs(secs + jitter)
    WIN.flip()
    return(fixation)

def play_tone(WIN, MARKER, TONE_DUR, freq, mark = None):
    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.play(when = now + 0.001)
    WaitSecs(0.001)
#    start = time.time()
    print(mark)
    MARKER.send(mark) if isinstance(mark, int) else None
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()
#    end = time.time()
#    print(f"tone len: {end-start}")

def display_cue_only(WIN, MARKER, TONE_DUR, mark):
    now = GetSecs()
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    WaitSecs(0.001)
    MARKER.send(mark)
    WIN.flip()
    WaitSecs(TONE_DUR)
    WIN.flip()

def play_adjusted_tone(WIN, TONE_DUR, freq):
    WIN.flip()
    now = GetSecs()
    snd = Sound(freq, secs = TONE_DUR)
    prompt = visual.TextStim(WIN, '*')
    prompt.draw()
    snd.play(when = now + 0.001)
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
    # Pick target freq
    index = random.randint(0, 1)
    freq = FREQS[index]
    print(f'freq: {freq}')

    mark_list = []
    for i in range(TONES_PER_TRIAL - 1):
        mark = get_mark(index, sound = True)
#        start = time.time()
        play_tone(WIN, MARKER, TONE_DUR, freq, mark)
        WaitSecs(ISI)
#        end = time.time()
#        print(f"Tone + ISI: {end-start}")
        mark_list.append(mark)

    mark = get_mark(index, sound = False)
    display_cue_only(WIN, MARKER, TONE_DUR, mark)
    WaitSecs(ISI)
    mark_list.append(mark)

    return(freq, mark_list)

def white_noise(secs):
    start = random.uniform(0, 8)
    stop = start + secs + random.uniform(-0.1, 0.1)
    snd = Sound('task/gaussianwhitenoise.wav', startTime = start, stopTime = stop, volume = 0.5)
    snd.play()
    WaitSecs(stop - start)
    
def play_displaced_target(WIN, MARKER, TONE_DUR, freq):
    displacement = random.randint(-10, 10)
    displaced_freq = freq + displacement
    play_tone(WIN, MARKER, TONE_DUR, displaced_freq)
    print(f'displaced_freq: {displaced_freq}')
    return(displaced_freq)
    
def pitch_adjustment(WIN, TONE_DUR, displaced_freq):
    keylist = ['up', 'down', 'return']

    while True:
        keys = event.getKeys(keyList = keylist)
        if 'return' in keys: # empty response not accepted
            break
        elif keys:
            if 'up' in keys:
                displaced_freq += 1
                play_adjusted_tone(WIN, TONE_DUR, displaced_freq)
            elif 'down' in keys:
                displaced_freq -= 1
                play_adjusted_tone(WIN, TONE_DUR, displaced_freq)

    response = displaced_freq
    return(response)

def feedback(WIN, freq, response, reward):
    diff = response - freq
    if diff == 0:
        reward += 0.5
        feedback = f"Spot on! You earned ${reward} for this block. Press 'enter' to continue."
    elif abs(diff) < 3:
        reward += 0.25
        feedback = f"Close enough! You were {abs(diff)} Hz above the target. You have earned ${reward} for this block. Press 'enter' to continue."
    elif diff >= 3:
        feedback = f"You were {abs(diff)} Hz above the target. Press 'enter' to continue."
    elif diff <= 3:
        feedback = f"You were {abs(diff)} Hz below the target. Press 'enter' to continue."

    display_instructions(WIN, feedback)    
    return(diff, reward)

def broadcast(n_tones, var):
    if not isinstance(var, list):
        broadcasted_array = [var]*n_tones
    return(broadcasted_array)

def write_log(LOG, TONES_PER_TRIAL, seed, SUB_NUM, BLOCK_NUM, trial_num, mark, freq, ISI, displaced_freq, response, diff, reward):
    print("Writing to log file")
    d = {
        'seed': broadcast(TONES_PER_TRIAL, seed),
        'sub_num': broadcast(TONES_PER_TRIAL, SUB_NUM),
        'block_num': broadcast(TONES_PER_TRIAL, BLOCK_NUM),
        'trial_num': broadcast(TONES_PER_TRIAL, trial_num),
        'tone_num' : list(range(1, TONES_PER_TRIAL + 1)),
        'heard' : [True]*(TONES_PER_TRIAL-1) + [False],
        'mark': mark,
        'freq': broadcast(TONES_PER_TRIAL, freq),
        'displaced_freq': broadcast(TONES_PER_TRIAL, displaced_freq),
        'response': broadcast(TONES_PER_TRIAL, response),
        'diff': broadcast(TONES_PER_TRIAL, diff),
        'reward': broadcast(TONES_PER_TRIAL, reward),
        }
    df = pd.DataFrame(data = d)
    df.to_csv(LOG, mode='a', header = False, index = False)

def end(WIN, BLOCK_NUM, reward):
    if BLOCK_NUM == "0":
        display_instructions(WIN, "Congratulations for finishing the practice block. Let your experimenter know if you have any questions or if you would like to repeat this practice block. If you are ready, you will now move on to the 5 experiment blocks, each of which will have 30 trials. \n \n Press 'enter' to complete this block.")
    else:
        display_instructions(WIN, f"End of block! You earned a total of ${reward} for this block. Press 'enter' to complete this block and your experimenter will come and check on you.")

