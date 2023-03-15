# Point Subtraction Aggression Paradigm
# Developers: Ramiro Reyes

# An adapted version of the PSAP-FS task (Golomb et al., 2007) written with PsychoPy.
# This experiment is a computerized, laboratory-based measure of reactive aggression.

# In every turn, participants choose between three actions: earn, protect, deduct.
# Earning allows to get one point after a certain amount of button presses (30 in this
# setup).
# Protect allows them to avoid any negative effects impacting their score for some time 
# (10 presses, 4-5.8s of protection in the current setup).
# Deduct allows them to remove one point from the "opponent" (after 10 button presses),
# but this point is not added to their own score.

# It involves deception, since participants believe they are playing against an opponent
# which may steal points from them at some point and add them to their score. However, 
# all actions are automatic, regulated by internal clocks that trigger the "opponent's"
# action after a certain amount of time without Deduct/Protect actions from the participant
# (set randomly to a 6-60s uniform interval after each event).

# The fact that the Deduct action doesn't add any points to the score, allows us to label
# these responses as aggressive, since they are only motivated by retaliation, without other
# cofounded value.

# The task is set to last around 25 min (it ends after the last choice, so it may extend a
# few seconds after the timer is exhausted). We incorporated a connection screen to help
# with the deception aspect of the task.

# Besides the original condition, we added a "fear/uncertainty" scenario to measure the 
# effects on the Protect action, by telling the participant that a random glitch may reduce
# their points by half at some time during the task.

# We also include a neutral condition that has no adverse events at all.

# It is based on:
# Golomb, A., Cortez-Perez, M., Jaworski, B., Mednick, S. & Dimsdale, J. (2007).
# Point Subtraction Aggression Paradigm: Validity of a Brief Schedule of Use.
# Violence and Victi, 22(1), 95-102.

# IMAGE CREDITS:
# All stimulus images from png images were downloaded with a premium license from Freepik (https://www.freepik.com)
# Avatar siluhettes: Rwdd_Studios - Freepik.com (Wild animals silhouettes collection - https://www.freepik.com/free-vector/wild-animals-silhouettes-collection_1043406.htm)
# Action icons: Redzen - Freepik.com (Signs and pictograms in buttons - https://www.freepik.com/free-vector/signs-and-pictograms-in-buttons_37210218.htm)

# Glitch icon: Freepik (Glitch geometric shape collection - https://www.freepik.com/free-vector/glitch-geometric-shape-collection_4057922.htm)
# Shield icon: Freepik (Pack of golden shields with ornaments - https://www.freepik.com/free-vector/pack-of-golden-shields-with-ornaments_1077660.htm)
# Steal icon: User1558154 - Freepik.com (Hacker with laptop - https://www.freepik.com/free-vector/hacker-with-laptop-hacker-attack-phishing-and-fraudvector-stock-illustration_34533105.htm)

# IMPORT LIBRARIES
from doctest import FAIL_FAST
import random
from psychopy import core, event, gui, visual
import datetime
import os
import glob
import pandas as pd
import numpy as np
from tkinter import messagebox

# BASE SETUP 
## Base paths
DIR_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_DATA = os.path.join(DIR_BASE, "data", "psap")
DIR_DSET = os.path.join(DIR_BASE, "data", "setup")
DIR_INST = os.path.join(DIR_BASE, "instructions")
DIR_FIGS = os.path.join(DIR_BASE, "figures")
DIR_STIM = os.path.join(DIR_FIGS, "stim")
DIR_FSET = os.path.join(DIR_FIGS, "setup")

## Image paths
BUTTON_LIST = glob.glob(os.path.join(DIR_STIM, "button*.png"))
AVATAR_LIST = glob.glob(os.path.join(DIR_STIM, "avatar*.png"))

SHIELD  = os.path.join(DIR_STIM, "shield.png")
PROFILE = os.path.join(DIR_STIM, "player_profile.png")

## Timing
clock = core.monotonicClock

## Dialog to enter experiment information
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
        exp_info["participant_id"] =  9999
    
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

## Define behavior for practice and normal runs
PLAYER_NAME = int(exp_info["participant_id"])

if test_run == True:
    exp_info["Participant ID"] = "practice"
    DIR_DATA = os.path.join(DIR_BASE, "data", "tests")
    TASK_DURATION = 90
    OPPONENT_NAME = "PRACTICE"

elif test_run == False:
    TASK_DURATION = 1500
    OPPONENT_NAME = int(exp_info["participant_id"]) + 2

if condition == "A":
    INCIDENT = os.path.join(DIR_STIM, "steal.png")
    
else:
    INCIDENT = os.path.join(DIR_STIM, "glitch.png")

# BASE STIM SETUP
## Window settings
WIN_WIDTH  = 1920
WIN_HEIGHT = 1080

win = visual.Window(
    size    = (WIN_WIDTH, WIN_HEIGHT),
    units   = "pix",
    color   = "#666666",
    fullscr = False
)

## Mouse component
mouse = event.Mouse(win = win)

## Define controls
KEY_NAME_LIST = ["S", "H", "L"]
KEY_LIST      = ["s", "h", "l"]
KEY_QUIT      = "escape"
ACTION_LIST   = ["Earn", "Deduct", "Protect"]
KEY_NEXT      = "return"

## Randomly assign buttons and icons to actions
random.shuffle(ACTION_LIST)
random.shuffle(BUTTON_LIST)

MSG_LIST = [f"Press {KEY_NAME_LIST[0]} to {ACTION_LIST[0]}",
            f"Press {KEY_NAME_LIST[1]} to {ACTION_LIST[1]}",
            f"Press {KEY_NAME_LIST[2]} to {ACTION_LIST[2]}"]

## Define and initialize csv file to dump data
PSAP_FILE = os.path.join(DIR_DATA, "%s-%s-%s-%s" % ("psap", exp_info["participant_id"], condition, exp_info["date_time"]) + ".csv")
psap_log = open(PSAP_FILE, "w")
psap_log.write("id, condition, color_01, color_02, color_03, action_01, action_02, action_03, choice, n_incidents, t_last_incident, start, end\n")

## Text settings
CONTROL_SIZE = 50
SCORE_SIZE   = 60
N_KEY_SIZE   = 50
SUMMARY_SIZE = 80

SHIELDED_COLOR = "#93FAEE"
LOST_COLOR     = "#FFA6A3"
EARNINGS_COLOR = "#ABFF94"
SUMMARY_COLOR  = "#F7E759"

## Stim settings
BUTTON_COLORS = ["#9E005D", "#2E5892", "#F7931E"]

BUTTON_SIZE  = [250, 250]
STATUS_SIZE  = [100, 90]
AVATAR_SIZE  = [200, 200]
PROFILE_SIZE = [300, 300]

## Screen positions
BUTTON_POS = [[-500, 0],
              [0, 0],
              [500, 0]]

AVATAR_POS = [[-330,  170], [-110,  170], [110,  170], [330,  170],
              [-330,  -50], [-110,  -50], [110,  -50], [330,  -50],
              [-330, -270], [-110, -270], [110, -270], [330, -270]]

CTRL_POS = [[BUTTON_POS[0][0], BUTTON_POS[0][1] - 200],
            [BUTTON_POS[1][0], BUTTON_POS[1][1] - 200],
            [BUTTON_POS[2][0], BUTTON_POS[2][1] - 200]]

SCORE_POS  = [0, BUTTON_POS[0][1] + 370]
COUNT_POS  = [SCORE_POS[0], SCORE_POS[1] - 70]

KEY_POS    = [SCORE_POS[0], -250]
N_KEY_POS  = [KEY_POS[0] + 50, KEY_POS[1] - 70]

STATUS_POS = [SCORE_POS[0] - 135, COUNT_POS[1] - 5]

# DEFINE OBJECTS TO DRAW
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

avatar_message = visual.TextStim(
    win,
    text      = "Click to choose your avatar",
    color     = "White",
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [0, 350],
    wrapWidth = 1500
)

wait_connection = visual.TextStim(
    win,
    text      = "Please Wait\n\nEstablishing connection...",
    color     = "White",
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [0, 250],
    wrapWidth = 1500
)

opponent_mesage = visual.TextStim(
    win,
    text      = f"Player {OPPONENT_NAME} has connected!",
    color     = "White",
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [0, -350],
    wrapWidth = 1500
)

wait_players = visual.TextStim(
    win,
    text      = "Waiting for players..",
    color     = "White",
    height    = SCORE_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [0, 300],
    wrapWidth = 1500
)

ready_control = visual.TextStim(
    win,
    text      = "Press ENTER when you are ready",
    color     = "White",
    height    = SCORE_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [0, 200],
    wrapWidth = 1500
)

ready_opponent = visual.TextStim(
    win,
    text      = f"Player {OPPONENT_NAME}\nis ready!",
    color     = "White",
    height    = CONTROL_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [550, -100],
    wrapWidth = 1500
)

ready_player = visual.TextStim(
    win,
    text      = f"Player {PLAYER_NAME}\nis ready!",
    color     = "White",
    height    = CONTROL_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [-550, -100],
    wrapWidth = 1500
)

launch_message = visual.TextStim(
    win,
    text      = "Lauching task\nPlease wait...",
    color     = "White",
    height    = SUMMARY_SIZE,
    units     = "pix",
    alignText = "center",
    pos       = [0, 200],
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

avatar_a = visual.ImageStim(
    win   = win,
    size  = AVATAR_SIZE
)

profile_opponent = visual.ImageStim(
    win   = win,
    image = PROFILE,
    pos   = [250, -100],
    size  = PROFILE_SIZE
)

profile_player = visual.ImageStim(
    win   = win,
    pos   = [-250, -100],
    size  = PROFILE_SIZE
)

### List of possible avatars 
avatar_l = avatar_k = avatar_j = avatar_i = avatar_h = avatar_g = avatar_f = avatar_e = avatar_d = avatar_c = avatar_b = avatar_a

AVATARS = [avatar_a, avatar_b, avatar_c, avatar_d, avatar_e, avatar_f, 
           avatar_g, avatar_h, avatar_i, avatar_j, avatar_k, avatar_l]

# DEFINE TASK ROUTINES
## Connection stage
### Avatar selection
def choose_avatar(icons =  AVATARS, player_frame = profile_player):
    show_images = True

    while show_images == True:
        for iImage, avatar in enumerate(icons):
            avatar.setImage(AVATAR_LIST[iImage])
            avatar.setPos(AVATAR_POS[iImage])
            avatar.clicked = False
            avatar.draw()
        
            if mouse.isPressedIn(avatar, buttons=[0]):
                player_frame.setImage(avatar.image)
                show_images = False
        
        avatar_message.draw()

        win.flip()
    
    core.wait(0.4)

### Wait for connection from other player
def connection_screen(wait_time = 3):
    wait_connection.autoDraw = profile_player.autoDraw = True
    win.flip()
    core.wait(wait_time)
    profile_opponent.draw()
    opponent_mesage.draw()
    win.flip()
    core.wait(wait_time-1)
    wait_connection.autoDraw = profile_player.autoDraw = False
    

### Wait for players to be ready
def ready_screen(wait_time = 2):
    wait_players.autoDraw = ready_control.autoDraw = profile_player.autoDraw = profile_opponent.autoDraw = True    
    profile_player.opacity = profile_opponent.opacity = 0.5    
    win.flip()
    core.wait(wait_time/2)
    profile_opponent.opacity = 1
    ready_opponent.autoDraw = True
    win.flip()
    event.waitKeys(keyList = ["return"])
    core.wait(wait_time/5)
    profile_player.opacity = 1
    ready_player.autoDraw = True
    win.flip()
    core.wait(wait_time)
    wait_players.autoDraw = ready_control.autoDraw = False
    win.flip()

### Launch the task
def launcher_screen(wait_time = 3):
    launch_message.draw()
    win.flip()
    core.wait(wait_time)
    profile_opponent.autoDraw = profile_player.autoDraw = ready_opponent.autoDraw = ready_player.autoDraw = False
    win.flip()

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
    score_counter.setText(f"{score:.2f}")
    score_counter.color    = color
    score_counter.size     = size
    score_text.autoDraw    = True
    score_counter.autoDraw = True
    score_counter.bold     = bold

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
    control_text.pos       = CTRL_POS[action]
    control_text.wrapWidth = BUTTON_SIZE[0]
    
    control_text.autoDraw  = True
    button.autoDraw = True

### Key press counter
def display_action_count(action, count, color = "White", size = N_KEY_SIZE):
    action_text.pos = [BUTTON_POS[ACTION_LIST.index(action)][0] - 25, BUTTON_POS[ACTION_LIST.index(action)][1] + 180]
    
    action_counter.setText(f"{count}")
    action_counter.color = color
    action_counter.size  = size
    action_counter.pos   = [BUTTON_POS[ACTION_LIST.index(action)][0] + 150, BUTTON_POS[ACTION_LIST.index(action)][1] + 180]
    
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
                button.autoDraw       = False
                threshold_met         = True

## Final summary
## Shows final score
def show_summary(score, practice = False):
    if practice == True:
        final_message.setText("End of the Practice Round")
        final_message.pos = [0, 100]
        final_message.draw()
       
        final_message.setText("Please notify the experimenter")
        final_message.pos = [0, 0]
        final_message.draw()
    
    else:
        final_message.setText("This is the end of this task")
        final_message.pos = [0, 100]
        final_message.draw()

        final_result.setText(f"Total Score: {score:.2f}")
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
    incident_message.pos   = [0, 100]
    incident_message.draw()

# MAIN ROUTINE
def psap():
    if test_run == False:
        choose_avatar(icons =  AVATARS, player_frame = profile_player)        

        ### wait for connection
        connection_screen()

        ### Wait for players to be ready
        ready_screen()

        ### Launch task
        launcher_screen()

    ## Initialize the event states and counters
    task_finished = False
    shielded      = False
    
    incident_counter = 0
    incident_time    = 0

    score = 0

    ## Define event time thresholds
    ### Practice rounds get fixed timers
    if test_run == False:
        
        ### Opponent steals
        if condition == "A":
            adverse_time_threshold = random.uniform(6, 60)
        
        ### Random glitch
        elif condition == "B":
            adverse_time_threshold = random.uniform(400, 500)
        
        ### Neutral, no negative events
        elif condition == "C":
            adverse_time_threshold = 100000
    
        shield_time_threshold = random.uniform(4, 5.8)
        
    elif test_run == True:
        adverse_time_threshold = 20
        shield_time_threshold  = 4

    ## Define clocks for task events
    task_clock    = core.Clock()
    shield_clock  = core.Clock()
    adverse_clock = core.Clock()

    ## Main loop runs for the amount of time defined as task duration    
    ### Each decision counts as a trial in this setup
    while not task_finished:
        trial_start_time = task_clock.getTime()
        outcome_interval = random.uniform(0.9, 1.1) #how long to display result
        
        ### End task trigger
        if trial_start_time > TASK_DURATION:
            task_finished = True

        ### Steal/Glitch trigger
        ### Both the timer and threshold for adverse events are reset 
        ### after the negative state is triggered.
        if adverse_clock.getTime() > adverse_time_threshold and shielded == False:
            incident_counter += 1
            incident_time = task_clock.getTime()

            ### Adverse event in actual experiment
            if test_run == False:
            
                ### Opponent steals
                if condition == "A":
                    score -= 1
                    show_incident(f"Player {OPPONENT_NAME}\nstole from you!", LOST_COLOR) 
                    adverse_time_threshold = random.uniform(6, 60)
                
                ### Glitch halves points
                elif condition == "B":
                    show_incident(f"System Error! You lost {score/2:.2f} points", LOST_COLOR) 
                    score = score/2
                    adverse_time_threshold = random.uniform(400, 500)

                ### Show outcome
                incident_icon.autoDraw = True
                display_score(score, color = LOST_COLOR, size = SCORE_SIZE, bold = True)
                win.flip()

                core.wait(outcome_interval)

                incident_icon.autoDraw = False
                adverse_clock.reset()

            ### Adverse event during practice
            ### This is designed to show both the glitch and steal scenarios
            ### Regardless of the conditions chose, this is triggered
            elif test_run == True:
                
                ### Alternate between steal and glitch
                if incident_counter % 2 == 0:
                    score -= 1
                    show_incident(f"Participant {OPPONENT_NAME}\nstole from you!", LOST_COLOR) 
                    adverse_time_threshold = 20
                    incident_icon.setImage(os.path.join(DIR_STIM, "steal.png"))
                
                else:
                    show_incident(f"System Error! You lost {score/2:.2f} points", LOST_COLOR) 
                    score = score/2
                    adverse_time_threshold = 20
                    incident_icon.setImage(os.path.join(DIR_STIM, "glitch.png"))

                ### Show outcome 
                incident_icon.autoDraw = True
                display_score(score, color = LOST_COLOR, size = SCORE_SIZE, bold = True)
                win.flip()
                
                core.wait(outcome_interval)
                
                incident_icon.autoDraw = False
                adverse_clock.reset()
            
        ### Reset shield timer and hide icon after protection timeout
        ### This is only triggered when there is a shield in the screen
        if shield_clock.getTime() > shield_time_threshold and shielded == True: 
            shield_time_threshold = random.uniform(4.5, 5.5)
            shield_icon.autoDraw  = False
            shield_clock.reset()
            shielded = False

        ### Show decision screen
        ### Participant can choose one of three actions
        display_controls(ACTION_LIST)
        display_score(score)
        win.flip()

        ### Wait for participant input
        key_response = event.waitKeys(keyList = KEY_LIST + [KEY_QUIT])

        ### Option to quit the task
        if key_response[0] == KEY_QUIT:  
            return
        
        action = key_press_action(key_response[0])

        ### Start press counter
        n_pressed = 1
        
        ### Define the number of times a button needs to be pressed
        ### to trigger the specific action.
        if action == "Earn":
            press_threshold = 30
        
        else:
            press_threshold = 10

        ### Show the pressing action screen
        ### This hides the other buttons and shows the counter until
        ### the press threshold is met
        action_trigger(action, n_pressed, press_threshold)
        
        ### Get time once the action is completed
        trial_stop_time = clock.getTime()

        ### Gather data and record on file
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

        ### Display action outcome
        ### Choosing to protect or deduct reset the adverse event clock
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
            show_incident("You deducted 1 point\nfrom your opponent!", SUMMARY_COLOR)
            win.flip()
            adverse_clock.reset()

        ### ITI
        core.wait(outcome_interval)

    ## Show final score
    show_summary(score, test_run)
    psap_log.close()

def main():    
    psap()
    win.close()
    core.quit()

if __name__ == "__main__":
    main()
