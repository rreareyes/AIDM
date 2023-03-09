# Cumulative Risk Card Paradigm
#Developers: Ramiro Reyes, Rajasi Desai
#Based on version developed by Hannah Sophie Heinrichs
#https://github.com/hsx1/bart_task

# A modified version of the Balloon Analog Risk Task (BART) written with PsychoPy.
# This experiment is a computerized, laboratory-based measure that involves actual
# risky behavior for which, similar to real-world situations, riskiness is rewarded
# up until a point at which further riskiness results in poorer outcomes.
# Participants complete 90 trials where they draw cards from a deck to obtain points.
# After each draw, the points get into a temporary bank. Each deck contains a bad card 
# that if drawn, ends the draws from that deck and sets the pot to 0, losing all the 
# temporaty gains. The participant then must choose if they want to draw more cards
# to increase the pot or stop drawing and cash out what they have accumulated so far
# and move on to the next deck. 

# This task addresses some methodological considerations from the original BART task:
# - It maintains the EV of every drawing choice constant, increasing the amount of points
#   that participants can earn with every draw.
# - Makes the decision horizon visible to participants, i.e., they always know how many 
#   cards are left in the deck, therefore the associated risk to drawing a card.

# It is based on:
# Lejuez, C. W., Read, J. P., Kahler, C. W., Richards, J. B., Ramsey, S. E., Stuart, G. L., ... & Brown, R. A. (2002).
# Evaluation of a behavioral measure of risk taking: the Balloon Analogue Risk Task (BART).
# Journal of Experimental Psychology: Applied, 8(2), 75-84. http://dx.doi.org/10.1037/1076-898X.8.2.75
# source: http://www.impulsivity.org/measurement/BART

from doctest import FAIL_FAST
import random
from psychopy import core, data, event, gui, visual
import datetime
import os
import glob
import math
import pandas as pd
import numpy as np

# SETUP 
## Ensure that relative paths start from the same directory as this script
DIR_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_DATA = os.path.join(DIR_BASE, "data", "crcp")
DIR_SEQ  = os.path.join(DIR_BASE, "data", "setup")
DIR_INST = os.path.join(DIR_BASE, "instructions")
DIR_FIGS = os.path.join(DIR_BASE, "figures")
DIR_STIM = os.path.join(DIR_FIGS, "stim")
DIR_FSET = os.path.join(DIR_FIGS, "setup")

# Obtain participant and setup information
clock = core.monotonicClock
DECK_ISI = random.uniform(0.8, 1)

exp_info = {"experiment_name":"AIDM-CRCP",
            "date_time":str(datetime.datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-"),
            "psychopyVersion":"3.2.4"}

setup_dialog = gui.Dlg(title = exp_info["experiment_name"]) 
setup_dialog.addField("Participant ID")
setup_dialog.addField("Practice?", choices=("Yes", "No"))                     
response = setup_dialog.show()

if(setup_dialog.OK):
    exp_info["participant_id"] = response[0]
    test_run    = response[1] == "Yes"
else:
    core.quit() # user pressed cancel

# Define behavior for practice and normal runs
if test_run == True:
    N_TRIALS  = 2  #number of decks of each type
    exp_info["Participant ID"] = "practice"
    DIR_DATA = os.path.join(DIR_BASE, "data", "tests")
elif test_run == False:
    N_TRIALS = 30

# Define and initialize csv file to dump data
CRCP_FILE = os.path.join(DIR_DATA, "%s-%s-%s" % ("crcp", exp_info["participant_id"], exp_info["date_time"]) + ".csv")
crcp_log = open(CRCP_FILE, "w")
crcp_log.write("id, deck_number, deck_id, risk, color, card, draw_value, pot, draw, choice, failed, start, end\n")

# Window and stimulus sizes
WIN_WIDTH = 1920
WIN_HEIGHT = 1080

CARD_SIZE  = (250, 357)
DECK_SIZE  = (250, 357)
TOKEN_SIZE = (242.5, 300)
BANK_SIZE  = (270, 275)

# Image paths
DECK_LIST  = glob.glob(os.path.join(DIR_STIM, "deck*.png"))
CARD_LIST  = glob.glob(os.path.join(DIR_STIM, "card*.png"))
BACK_LIST  = glob.glob(os.path.join(DIR_STIM, "back*.png"))
TOKEN_LIST = glob.glob(os.path.join(DIR_STIM, "tokens*.png"))

BAD_CARD_IMAGE = os.path.join(DIR_STIM, "nuke.png")
BANK_IMAGE     = os.path.join(DIR_STIM, "bank.png")

# Randomly assign deck colors to risk levels
color_index = [0, 1, 2]
random.shuffle(color_index)
shuffled_decks  = list(map(DECK_LIST.__getitem__, color_index))
shuffled_tokens = list(map(TOKEN_LIST.__getitem__, color_index))
shuffled_backs  = list(map(BACK_LIST.__getitem__, color_index))

# Text settings
DECISION_SIZE   = 45
DECISION_OFFSET = DECK_SIZE[1]/1.2

OUTCOME_SIZE = 50
CONTROL_SIZE = 35
COUNTER_SIZE = 50
SUMMARY_SIZE = 60
CHOICE_SIZE  = 60

SUMMARY_COLOR  = "#93FAEE"
LOST_COLOR     = "#FFA6A3"
EARNINGS_COLOR = "#ABFF94"
CHOICE_COLOR   = "#F7E759"

# Animation settings
DECK_HOFFSET = -400
DECK_VOFFSET = 0

START_ANGLE = -90
FINAL_ANGLE = 0
ANGLE_INC   = 4

MOV_STEPS = len(range(START_ANGLE, FINAL_ANGLE, ANGLE_INC))
POS_INC   = 17.5

# Task settings
MAX_DRAWS   = [37, 25, 17]  # three risk types
TOTAL_DECKS = len(MAX_DRAWS) * N_TRIALS
BREAKS      = range(19, 89, 20)

# Define stimulus sequences and deck settings
DECK_SEQUENCE = np.repeat(range(0, len(MAX_DRAWS)), N_TRIALS)

LOW_DECK  = pd.read_csv(os.path.join(DIR_SEQ, "crcp_low_risk.csv"))
MED_DECK  = pd.read_csv(os.path.join(DIR_SEQ, "crcp_med_risk.csv"))
HIGH_DECK = pd.read_csv(os.path.join(DIR_SEQ, "crcp_high_risk.csv"))

DECK_INFO = [LOW_DECK, MED_DECK, HIGH_DECK]

# Define response keys
KEY_DRAW    = "space"
KEY_CASHOUT = "return"
KEY_QUIT    = "escape"

# Define objects to draw
# Window
win = visual.Window(
    size    = (WIN_WIDTH, WIN_HEIGHT),
    units   = "pix",
    color   = "#666666",
    fullscr = False
)

# Text objects
decision_text = visual.TextStim(
    win,
    color  = "White",
    height = DECISION_SIZE,
    units  = "pix"
)

control_text = visual.TextStim(
    win,
    color  = "White",
    height = CONTROL_SIZE,
    units  = "pix"
)

outcome_text = visual.TextStim(
    win,
    color  = "White",
    height = OUTCOME_SIZE,
    units  = "pix"
)

summary_text = visual.TextStim(
    win,
    height = SUMMARY_SIZE,
    units  = "pix"
)

counter_text = visual.TextStim(
    win,
    color  ="White",
    height = COUNTER_SIZE,
    units  ="pix"
)

card_counter = visual.TextStim(
    win,
    color       = "White",
    height      = 0.08,
    pos         = (-0.2, -0.9),
    alignText   = "right",
    units       = "norm",
    anchorHoriz = "right",
    anchorVert  = "bottom"
)

# Image objects
total_bank = visual.ImageStim(
    win   = win,
    image = BANK_IMAGE,
    size  = BANK_SIZE,
    pos   = [0, -10]
)

card_back = visual.ImageStim(
    win  = win,
    size = DECK_SIZE
)

card_front = visual.ImageStim(
    win  = win,
    size = CARD_SIZE,
    pos  = [DECK_HOFFSET + (MOV_STEPS * POS_INC), DECK_VOFFSET + 10],
    ori  = math.radians(FINAL_ANGLE)
)

deck_stack = visual.ImageStim(
    win  = win,
    size = DECK_SIZE,
    pos  = [DECK_HOFFSET, DECK_VOFFSET],
    ori  = math.radians(START_ANGLE)
)

token_stack = visual.ImageStim(
    win  = win,
    size = TOKEN_SIZE,
    pos  = [-DECK_HOFFSET, DECK_VOFFSET-30]
)

# Animation
# Drawing a card each turn
def draw_card(front_image, deck, draw_value):
    # move the back of the card from left to right
    step = 0
    card_front.image  = front_image
    deck_stack.image  = shuffled_decks[deck]
    card_back.image   = shuffled_backs[deck]
    token_stack.image = shuffled_tokens[deck]

    for angle in range(START_ANGLE, FINAL_ANGLE, ANGLE_INC):
        deck_stack.draw()
        token_stack.draw()
        card_back.ori = math.radians(angle)
        card_back.pos = [DECK_HOFFSET + step, DECK_VOFFSET + 10]
        card_back.draw()
        win.flip()
        step += POS_INC
        if angle == max(range(START_ANGLE, FINAL_ANGLE, ANGLE_INC)):
            deck_stack.draw()
            token_stack.draw()
            card_front.draw()
            wait_time = random.uniform(0.5, 0.6)
            if draw_value == 0:
                drawText(counter_text, (0, DECISION_OFFSET), "YOU LOST THE POT!", "center", True)
            else:
                drawText(counter_text, (0, DECISION_OFFSET), "Pot increased by", "center", True)
                drawText(counter_text, (0, DECISION_OFFSET-50), "{:.2f}".format(draw_value), "center", True, CHOICE_COLOR)
                
            win.flip()
            core.wait(wait_time)
           
# Summary screen
def bank_summary(earnings, total, lost = False):
    if lost == False:
        temp_bank_color = SUMMARY_COLOR
    else:
        temp_bank_color = LOST_COLOR

    total_bank.draw()
    drawText(summary_text, (DECK_HOFFSET + 150, 250), "Collected:", "center", True)
    drawText(summary_text, (DECK_HOFFSET + 150, 180), "{:.2f}".format(earnings), "center", True, temp_bank_color)
    drawText(summary_text, (-DECK_HOFFSET - 150, 250), "Total:", "center", True)
    drawText(summary_text, (-DECK_HOFFSET - 150, 180), "{:.2f}".format(total), "center", True, EARNINGS_COLOR)
    

def drawText(TextStim, pos, txt, alignment="right", bold = False, color = "white"):
    """Takes a PsychoPy TextStim and updates position and text before drawing the stimulus."""
    TextStim.pos = (pos)
    TextStim.setText(txt)
    TextStim.alignText = alignment
    TextStim.bold = bold
    TextStim.color = color
    TextStim.wrapWidth=1000 
    TextStim.draw()

def decisionStage(deck_image, tokens_image, tempPoints, currentValue, cards_left):
    """Displays decision scenario with the value of taking action and points accrued in the deck"""
    deck_stack.setImage(deck_image)
    token_stack.setImage(tokens_image)
    deck_stack.draw()
    token_stack.draw()    
    
    drawText(counter_text, (0, DECISION_OFFSET), "Cards left:", "center", True)
    drawText(counter_text, (0, DECISION_OFFSET-50), "{:d}".format(cards_left), "center", True, CHOICE_COLOR)

    drawText(decision_text, (DECK_HOFFSET, -220), "Draw value:", "center", True)
    drawText(decision_text, (DECK_HOFFSET, -270), "{:.2f}".format(currentValue), "center", True, CHOICE_COLOR)
    drawText(control_text, (DECK_HOFFSET, -370), "Press SPACE\nto draw a card", "center")

    drawText(decision_text, (-DECK_HOFFSET, -220), "Pot value:", "center", True)
    drawText(decision_text, (-DECK_HOFFSET, -270), "{:.2f}".format(tempPoints), "center", True, CHOICE_COLOR)
    drawText(control_text, (-DECK_HOFFSET, -370), "Press ENTER\nto collect pot", "center")
        
    win.flip()
    deck_stack.setAutoDraw(False)

def crcp():
    """Execute experiment"""
    random.shuffle(DECK_SEQUENCE)
    permanent_bank = 0
    # Iterate through decks (each deck is considered as a trial)
    for iTrial, trial in enumerate(DECK_SEQUENCE):
        
        # Reset counters
        n_draws = 0 
        temporal_pot = 0  
        nuke = False #bad card drawn ends the trial
        
        continue_drawing = True #while trigger, when false trial ends
        card_displayed   = "none"
        # Deck starting settings
        deck_image  = shuffled_decks[trial]
        token_image = shuffled_tokens[trial] #temporal pot image
        deck_risk   = MAX_DRAWS[trial] #cards in deck
        deck_data   = DECK_INFO[trial]
        deck_color  = os.path.basename(deck_image).split(".")[0].split("_")[2]
        deck_id     = trial

        # Obtain a list of good card images to show
        # We have a finite number, so if the deck asks for more than the total
        # number of card images in stock, we sample with replacement
        if len(CARD_LIST) > deck_risk:
            card_sequence = random.sample(CARD_LIST, deck_risk)
        else:
            card_sequence = random.choices(CARD_LIST, k=deck_risk)
        
        # Draw cards from the deck
        while continue_drawing and not nuke:
            cards_left = deck_risk - n_draws
            draw_value = deck_data.rw_round[n_draws] 
            
            # Display deck and temporal pot
            decisionStage(deck_image, token_image, temporal_pot, draw_value, cards_left)
        
            trial_start_time = clock.getTime() #start time
            
            # Wait for response
            respond = event.waitKeys(keyList=[KEY_DRAW, KEY_CASHOUT, KEY_QUIT], maxWait = 5)

            # No response - continue to next deck
            if not respond:
                drawText(summary_text, (0, 50), "You've waited too long!", "center")
                drawText(summary_text, (0, -50), "You LOST the pot", "center", True, LOST_COLOR)
                win.flip()
                core.wait(1.2)
                temporal_pot = 0
                permanent_bank += temporal_pot
                bank_summary(temporal_pot, permanent_bank, lost = True)
                
                # Database fillers for invalid/empty responses
                bad_card_drawn  = 99 
                choice_code     = 99
                card_displayed  = "none"
                trial_stop_time = 0
                
                if iTrial in BREAKS: # Break every certain amount of trials
                    drawText(summary_text, (0, -220), "You can take a break now", "center")
                    drawText(summary_text, (0, -350), "Press ENTER\nto continue", "center")
                    win.flip()
                    event.waitKeys(keyList=KEY_CASHOUT)
                
                else:
                    win.flip()
                    core.wait(DECK_ISI)
                    
                continue_drawing = False
            elif respond[0] == KEY_QUIT:
                return

            # Cash-out key pressed
            elif respond[0] == KEY_CASHOUT:
                choice_code = 0
                bad_card_drawn = False
                permanent_bank += temporal_pot
                bank_summary(temporal_pot, permanent_bank, lost = False)
                
                if iTrial in BREAKS:
                    drawText(summary_text, (0, -220), "You can take a break now", "center")
                    drawText(summary_text, (0, -350), "Press ENTER\nto continue", "center")
                    win.flip()
                    event.waitKeys(keyList=KEY_CASHOUT)
                
                else:
                    win.flip()
                    core.wait(DECK_ISI)
                continue_drawing = False
                trial_stop_time = clock.getTime() #stop time
            
            # Draw key pressed
            elif respond[0] == KEY_DRAW:
                choice_code = 1
                n_draws += 1
                trial_stop_time = clock.getTime() #stop time
                bad_card_drawn = random.random() < 1.0 / (deck_risk - n_draws)
                
                # determine whether bad card is drawn or not
                if bad_card_drawn == True:
                    card_displayed = "bad"
                    temporal_pot = 0
                    permanent_bank += temporal_pot
                    draw_value = 0
                    draw_card(BAD_CARD_IMAGE, trial, draw_value)
                    nuke = True
                    bank_summary(temporal_pot, permanent_bank, lost = True)
                    
                    if iTrial in BREAKS:
                        drawText(summary_text, (0, -220), "You can take a break now", "center")
                        drawText(summary_text, (0, -350), "Press ENTER\nto continue", "center")
                        win.flip()
                        event.waitKeys(keyList=KEY_CASHOUT)
                    
                    else:
                        win.flip()
                        core.wait(DECK_ISI)                  
                else:
                    card_image = card_sequence[n_draws-1]
                    card_displayed = os.path.basename(card_image).split(".")[0].split("_")[1]
                    draw_card(card_image, trial, draw_value)
                    temporal_pot += draw_value
            
            # Organize data log and write into file
            temp_data = [str(exp_info["participant_id"]),
                         str(iTrial),
                         str(deck_id), 
                         str(deck_risk),
                         str(deck_color),
                         str(card_displayed),
                         str(draw_value),
                         str(temporal_pot),
                         str(n_draws),
                         str(choice_code),
                         str(bad_card_drawn),
                         str(trial_start_time),
                         str(trial_stop_time)]
            
            temp_data = ",".join(temp_data)
            temp_data = temp_data + "\n"
            crcp_log.write(temp_data)
        
    # Final message and earnings summary
    if test_run == True:
        drawText(summary_text, (0, 100), "End of the Practice Round", "center", True)
        drawText(summary_text, (0, 0), "Please notify the experimenter", "center", True)

    else:
        drawText(summary_text, (0, 100), "Well done! You banked a total of", "center", True)
        drawText(summary_text, (0, 0), "{:.2f} points".format(permanent_bank), "center", True, EARNINGS_COLOR)
        drawText(summary_text, (0, -100), "Thank you for your participation!", "center", True)

    crcp_log.close()
    win.flip()
    core.wait(4)
    return

def main():
    
    crcp()
    # quit experiment
    win.close()
    core.quit()

if __name__ == "__main__":
    main()
