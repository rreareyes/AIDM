from doctest import FAIL_FAST
import random
from psychopy import core, data, event, gui, visual
import datetime
import os
import glob
import sys
import string
import math
import pandas as pd
import numpy as np
from tkinter import messagebox


# SETUP 
## Ensure that relative paths start from the same directory as this script
DIR_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_DATA = os.path.join(DIR_BASE, "data", "psap")
DIR_DSET = os.path.join(DIR_BASE, "data", "setup")
DIR_INST = os.path.join(DIR_BASE, "instructions")
DIR_FIGS = os.path.join(DIR_BASE, "figures")
DIR_STIM = os.path.join(DIR_FIGS, "stim")
DIR_FSET = os.path.join(DIR_FIGS, "setup")

# Image paths
BUTTON_LIST = glob.glob(os.path.join(DIR_STIM, "button*.png"))
TOKEN_LIST  = glob.glob(os.path.join(DIR_STIM, "hex*.png"))

SHIELD = os.path.join(DIR_STIM, "shield.png")

# Obtain participant and setup information
clock = core.monotonicClock

exp_info = {"experiment_name":"AIDM-PSAP",
            "date_time":str(datetime.datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-"),
            "psychopyVersion":"3.2.4"}

setup_dialog = gui.Dlg(title = exp_info["experiment_name"]) 
setup_dialog.addField("Participant ID")
setup_dialog.addField("Condition", choices=("A", "B", "C"))
setup_dialog.addField("Practice?", choices=("Yes", "No"))
response = setup_dialog.show()

if(setup_dialog.OK):
    if response[0] == "":
        exp_info["participant_id"] =  0
    else:
        exp_info["participant_id"] = response[0]
    
    condition = response[1]
    test_run = response[2] == "Yes"
else:
    core.quit() # user pressed cancel

while True:
    try:
        int(exp_info["participant_id"])
        break
    except ValueError:
        print("ERROR: Only use numbers for the Participant ID")
        messagebox.showerror("ERROR:", "Only use numbers for the Participant ID")
        core.quit()

# Define behavior for practice and normal runs
if test_run == True:
    N_TRIALS = 1  # repetitions of risk
    exp_info["Participant ID"] = "practice"
    DIR_DATA = os.path.join(DIR_BASE, "data", "tests")
    TASK_DURATION = 200
elif test_run == False:
    N_TRIALS = 10
    TASK_DURATION = 1500

if condition == "A":
    INCIDENT = os.path.join(DIR_STIM, "steal.png")
    
else:
    INCIDENT = os.path.join(DIR_STIM, "glitch.png")

# Window settings
WIN_WIDTH  = 1920
WIN_HEIGHT = 1080

win = visual.Window(
    size    = (WIN_WIDTH, WIN_HEIGHT),
    units   = "pix",
    color   = "#666666",
    fullscr = False
)

# Define controls
KEY_NAME_LIST = ["S", "H", "L"]
KEY_LIST      = ["s", "h", "l"]
KEY_QUIT      = "escape"
ACTION_LIST   = ["Earn", "Deduct", "Protect"]
KEY_NEXT      = "return"

# Randomly assign buttons and icons to actions
random.shuffle(ACTION_LIST)
random.shuffle(BUTTON_LIST)

MSG_LIST = [f"Press {KEY_NAME_LIST[0]} to {ACTION_LIST[0]}",
            f"Press {KEY_NAME_LIST[1]} to {ACTION_LIST[1]}",
            f"Press {KEY_NAME_LIST[2]} to {ACTION_LIST[2]}"]

# Define and initialize csv file to dump data
PSAP_FILE = os.path.join(DIR_DATA, "%s-%s-%s-%s" % ("psap", exp_info["participant_id"], condition, exp_info["date_time"]) + ".csv")
psap_log = open(PSAP_FILE, "w")
psap_log.write("id, condition, color_01, color_02, color_03, action_01, action_02, action_03, choice, n_incidents, t_last_incident, start, end\n")

# Text settings
CONTROL_SIZE = 50
SCORE_SIZE   = 60
N_KEY_SIZE   = 50
SUMMARY_SIZE = 80

SHIELDED_COLOR = "#93FAEE"
LOST_COLOR     = "#FFA6A3"
EARNINGS_COLOR = "#ABFF94"
SUMMARY_COLOR  = "#F7E759"

BUTTON_COLORS = ["#9E005D", "#2E5892", "#F7931E"]

BUTTON_SIZE = [250, 250]
STATUS_SIZE = [100, 90]

BUTTON_POS = [[-500, 0],
              [0, 0],
              [500, 0]]

CTRL_POS = [[BUTTON_POS[0][0], BUTTON_POS[0][1] - 200],
            [BUTTON_POS[1][0], BUTTON_POS[1][1] - 200],
            [BUTTON_POS[2][0], BUTTON_POS[2][1] - 200]]

SCORE_POS  = [0, BUTTON_POS[0][1] + 370]
COUNT_POS  = [SCORE_POS[0], SCORE_POS[1] - 70]

KEY_POS    = [SCORE_POS[0], -250]
N_KEY_POS  = [KEY_POS[0] + 50, KEY_POS[1] - 70]

STATUS_POS = [SCORE_POS[0] - 125, COUNT_POS[1] - 5]

# Define objects to draw
## Text
control_text = visual.TextStim(
    win,
    color     = "White",
    height    = CONTROL_SIZE,
    units     = "pix",
    alignText = "center"
)

score_text = visual.TextStim(
    win,
    text      = "Score:",
    color     = "White",
    height    = SCORE_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = SCORE_POS
)

score_counter = visual.TextStim(
    win,
    units     = "pix",
    alignText = "center",
    pos       = COUNT_POS
)

action_text = visual.TextStim(
    win,
    text      = "Key presses:",
    color     = "White",
    height    = N_KEY_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = KEY_POS
)

action_counter = visual.TextStim(
    win,
    color     = "White",
    height    = N_KEY_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = N_KEY_POS
)

incident_message = visual.TextStim(
    win,
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    wrapWidth = 1500
)

final_message = visual.TextStim(
    win,
    color     = "White",
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    wrapWidth = 1500
)

final_result = visual.TextStim(
    win,
    color     = SUMMARY_COLOR,
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    wrapWidth = 1500
)

## Images
shield_icon = visual.ImageStim(
    win   = win,
    image = SHIELD,
    size  = STATUS_SIZE,
    pos   = STATUS_POS
)

button = visual.ImageStim(
    win   = win,
    size  = BUTTON_SIZE    
)

status_icon = visual.ImageStim(
    win   = win,
    size  = STATUS_SIZE,
    pos   = STATUS_POS
)

incident_icon = visual.ImageStim(
    win   = win,
    image = INCIDENT,
    size  = STATUS_SIZE,
    pos   = STATUS_POS
)

# Define functions to display stimuli/controls

## Main screen 
### Show actions and controls
def display_controls(actions):
    for iButton in range(len(actions)):
        button.setImage(BUTTON_LIST[iButton])
        button.pos = BUTTON_POS[iButton]
        control_text.setText(MSG_LIST[iButton])
        control_text.pos = CTRL_POS[iButton]
        control_text.wrapWidth = BUTTON_SIZE[0]
        control_text.draw()
        button.draw()

### Score counter        
def display_score(score, color = "White", size = SCORE_SIZE, bold = False):
    score_counter.setText(f"{score}")
    score_counter.color = color
    score_counter.size = size
    score_text.autoDraw = True
    score_counter.autoDraw = True
    score_counter.bold = bold

## Post-choice screen
## This continues until the participant presses the selected key a set
## number of times (determined by the threshold argument)

### Identify the action selected based on the key pressed
def key_press_action(key_pressed):
    action_dict = {"s": ACTION_LIST[0],
                   "h": ACTION_LIST[1],
                   "l": ACTION_LIST[2]}

    return action_dict.get(key_pressed, "Invalid")

### Show only the button corresponding to the action selected
def display_action(action):
    button.setImage(BUTTON_LIST[action])
    button.pos = BUTTON_POS[action]
    control_text.setText(MSG_LIST[action])
    control_text.pos = CTRL_POS[action]
    control_text.wrapWidth = BUTTON_SIZE[0]
    control_text.autoDraw = True
    button.autoDraw = True

### Key press counter
def display_action_count(action, count, color = "White", size = N_KEY_SIZE):
    action_text.pos = [BUTTON_POS[ACTION_LIST.index(action)][0] - 25, BUTTON_POS[ACTION_LIST.index(action)][1] + 180]
    action_counter.setText(f"{count}")
    action_counter.color = color
    action_counter.size = size
    action_counter.pos = [BUTTON_POS[ACTION_LIST.index(action)][0] + 150, BUTTON_POS[ACTION_LIST.index(action)][1] + 180]
    action_text.draw()
    action_counter.draw()

### Wrapper that keeps state until the key press threshold is met
def action_trigger(action, n_pressed, threshold = 10):
    display_action(ACTION_LIST.index(action))
    win.flip()
    threshold_met = False
    while not threshold_met:
        display_action_count(action, n_pressed)
        win.flip()

        pressed = event.waitKeys(keyList = KEY_LIST[ACTION_LIST.index(action)])
        if key_press_action(pressed[0]) == action:
            n_pressed += 1
            
            if n_pressed == threshold:
                control_text.autoDraw = False
                button.autoDraw = False
                threshold_met = True

## Final summary
# Shows final score and saves data
def show_summary(score):
    final_message.setText("This is the end of this task")
    final_message.pos = [0, 100]
    final_message.draw()
    final_result.setText(f"Total Score: {score}")
    final_result.pos = [0, 0]
    final_result.draw()
    final_message.setText("Thank you for participanting!")
    final_message.pos = [0, -100]
    final_message.draw()
    win.flip()
    event.waitKeys(5, "enter")

def show_incident(message, color):
    incident_message.setText(message)
    incident_message.color = color
    incident_message.pos = [0, 100]
    incident_message.draw()

# MAIN ROUTINE
def psap():
    task_finished = False
    task_clock = core.Clock()
    shield_clock = core.Clock()
    adverse_clock = core.Clock()
    shielded = False
    score = 0
    if condition == "A":
        adverse_time_threshold = random.uniform(6, 60)
    elif condition == "B":
        adverse_time_threshold = random.uniform(400, 500)
    elif condition == "C":
        adverse_time_threshold = 100000

    shield_time_threshold = random.uniform(4, 5.8)

    incident_counter = 0
    incident_time = 0
    oponent = int(exp_info["participant_id"]) + 2
    
    while not task_finished:
        trial_start_time = task_clock.getTime()
        
        if adverse_clock.getTime() > adverse_time_threshold and shielded == False:
            incident_counter += 1
            incident_time = task_clock.getTime()
            
            if condition == "A":
                score -= 1
                show_incident(f"Participant {oponent}\nstole from you!", LOST_COLOR) 
                adverse_time_threshold = random.uniform(6, 60)
            elif condition == "B":
                score -= 2
                show_incident("System Error!", LOST_COLOR) 
                adverse_time_threshold = random.uniform(400, 500)
            
            incident_icon.autoDraw = True
            display_score(score, color = LOST_COLOR, size = SCORE_SIZE, bold = True)
            win.flip()
            core.wait(random.uniform(1.5, 2))
            incident_icon.autoDraw = False
            adverse_clock.reset()
            
        if shield_clock.getTime() > shield_time_threshold: 
            shield_time_threshold = random.uniform(4, 5)
            shield_icon.autoDraw = False
            display_controls(ACTION_LIST)
            win.flip()
            shield_clock.reset()
            shielded = False
                
        display_controls(ACTION_LIST)
        display_score(score)
        win.flip()

        key_response = event.waitKeys(keyList = KEY_LIST + [KEY_QUIT])

        if key_response[0] == KEY_QUIT:  
            return
        
        action = key_press_action(key_response[0])

        n_pressed = 1

        action_trigger(action, n_pressed)
        trial_stop_time = clock.getTime()

        temp_data = [str(exp_info["participant_id"]),
                     str(condition), 
                     str(os.path.basename(BUTTON_LIST[0]).split(".")[0].split("_")[1]),
                     str(os.path.basename(BUTTON_LIST[1]).split(".")[0].split("_")[1]),
                     str(os.path.basename(BUTTON_LIST[2]).split(".")[0].split("_")[1]),
                     str(ACTION_LIST[0]),
                     str(ACTION_LIST[1]),
                     str(ACTION_LIST[2]),
                     str(key_response),
                     str(incident_counter),
                     str(incident_time),
                     str(trial_start_time),
                     str(trial_stop_time)]
        
        temp_data = ",".join(temp_data)
        temp_data = temp_data + "\n"
        psap_log.write(temp_data)

        if action == "Earn":
            score += 1
            display_score(score, color = EARNINGS_COLOR, size = SCORE_SIZE, bold = True)
            show_incident("You earned 1 point!", EARNINGS_COLOR)
            win.flip()
        elif action == "Protect":
            shield_icon.autoDraw = True
            display_score(score, color = SHIELDED_COLOR, size = SCORE_SIZE, bold = True)
            shielded = True
            show_incident("Your points are protected\nfor some time", SHIELDED_COLOR)
            win.flip()
            adverse_clock.reset()
            shield_clock.reset()
        elif action == "Deduct":
            show_incident("You deducted 1 point\nfrom your oponent!", SUMMARY_COLOR)
            win.flip()
            adverse_clock.reset()

        core.wait(random.uniform(1.5, 2))

    show_summary(score)
    psap_log.close()

def main():
    
    psap()
    # quit experiment
    win.close()
    core.quit()


if __name__ == "__main__":
    main()
