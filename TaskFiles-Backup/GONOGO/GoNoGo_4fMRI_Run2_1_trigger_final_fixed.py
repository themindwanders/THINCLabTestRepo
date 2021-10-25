#!/usr/bin/env python
# Changelog

# CHECK WITH CHARLOTTE IF I'M LOGGING DURATION CORRECTLY

#Import things we need
from psychopy import visual
from psychopy import core, event, gui, data, logging
import time
from psychopy.misc import fromFile
import os, csv
import numpy as np
import numpy.random
import random
from collections import deque

import glob, pygame, sys 
from psychopy.misc import fromFile

if sys.platform == 'linux2':
    sys.path.append('/groups/stimpc/ynicstim')
else:
    sys.path.append('M:/stimpc/ynicstim')

trig_collector = None

############################################# fMRI #############################################################

def setup_input(input_method):
    
    #If input_method is 'keyboard', we don't do anything
    #If input_method is 'serial', we set up the serial port for fMRI responses
    
    if input_method == 'keyboard':
        # Don't do anything
        resp_device = None
    elif input_method == 'serial':
        # Serial - we need to set it up
        import serial
        if sys.platform == 'linux2':
            port = '/dev/ttyS0'
        else:
            port = 'COM1'
        resp_device = serial.Serial(port=port, baudrate=9600)
        resp_device.setTimeout(0.0001)
    else:
        raise Exception('Unknown input method')
    return resp_device

def clear_buffer(input_method, resp_device):

    #Clear whichever buffer is appropriate for our input method

    if input_method == 'keyboard':
        # Clear the keyboard buffer
        event.clearEvents()
    else:
        # Clear the serial buffer
        resp_device.flushInput()

def get_response(input_method, resp_device, timeStamped):
    #if participants don't respond we will set up a null value so we don't get an error
    thisResp = None
    thisRT = np.nan
    if input_method == 'keyboard':
        for key, RT in event.getKeys(keyList = ['escape', 'q', 'left', 'right', 'space'], timeStamped = timeStamped):
            if key in ['escape','q']:
                print 'User Cancelled'
                print key
                if trig_collector:
                    trig_collector.endCollection()
                core.quit()
            else:
                thisResp = key
                thisRT = myClock.getTime()
    else:
        thisResp = resp_device.read(1)
        thisRT = timeStamped.getTime()
        if len(thisResp) == 0:
            thisResp = None
            thisRT = np.nan
        else:
            # Map button numbers to side
            ## Blue == 1, Green == 3
            if thisResp in ['1', '3']:
                thisResp = 'left'
            elif thisResp in ['2', '4']:
                thisResp = 'right'

        # Quickly check for a 'q' response on the keyboard to quit
        for key, RT in event.getKeys(keyList = ['escape', 'q'], timeStamped = timeStamped):
            if key in ['escape', 'q']:
                print 'User cancelled'
                if trig_collector:
                    trig_collector.endCollection()
                core.quit()
    return thisResp, thisRT


############################################Define all fMRI variables###############################################

#Implement absolute paths in any computer
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# This needs to be either keyboard or serial - we then setup the response device
input_method = 'serial'
resp_device = setup_input(input_method)

#let the script know if we are in the scanner or not (true/false)
In_scanner = True
slices_per_vol = 38

#Create dummy period (time needed for the scanner to collect 2 volumes)
Dummy_timer = core.CountdownTimer(10)

################################## Define all variables experiment ######################################

#collect participant info, create logfile
info = {'Subject':'test','Age':'','Gender':['male','female','other']}
infoDlg = gui.DlgFromDict(info, title = 'Subject details:', order = ['Subject','Age','Gender'])

# Set the sequence
orden = 'Sequence: Alpha - B C A'

#If user clicks OK continue with experiment and create a logfile with their details #else quite experiment
if infoDlg.OK: 
    logpath = 'log_file/%s_log_GoNoGo.csv' %(info['Subject'])
    fmri_logpath = 'log_file/%s_log_GoNoGo_fMRI_log.csv' %(info['Subject'])
    f = open(logpath, 'w+') # create log file
    f.write('%s_%s_%s\n' %(info['Subject'], info['Age'], info['Gender'])) # write participant info
    f.write('%s,\n' %(orden))
    f.write('Part_ID, Block, Condition, GO or NO, Item ID, Box Type, Correct Answer, Key, RT, Onset, Duration\n') # write headers for logfiles
    fmri_log=open(fmri_logpath, 'w+')#create fMRI logfile
    fmri_log.write('%s_%s_%s\n' %(info['Subject'], info['Age'], info['Gender'])) # write participant info
    fmri_log.write('Volume,Time\n')
else:
    print 'User Cancelled'
    core.quit()
    
#if participants don't respond we will set up a null value so we don't get an error
thisResp_go = 'no response'
thisResp_nogo = 'no response'
corrAns = ' '
thisRT_go = np.nan
thisRT_nogo = np.nan

# set up a stimulus window
myWin = visual.Window(size=(1280, 800), fullscr=True, allowGUI=False,winType='pyglet',
            monitor='testMonitor', units ='norm', screen=0, rgb=(1,1,1))

#set up some fonts. If a list is provided, the first font found will be used.
sans = ['Helvetica','Gill Sans MT', 'Arial','Verdana'] #use the first font found on this list

#set up instructions and clock (so you can time stamp duration or trials, RT etc..)
instrTxt1 = visual.TextStim(myWin,text="For this task, a series of words and pictures framed by a black box will appear in the centre of the screen. \
Your job is to press the left button every time a stimulus appears, except when that stimulus is an animal. Then, don't press anything. \n\
\nYou will be given around 1 second to respond to each stimulus, after which time, another one will appear. \n\
\nSometimes, instead of words or pictures, you will see a scrambled image framed by a box. In that case, your job is to press the left button \
on the keyboard every time a stimulus appear that is more slanted than the one that is normally presented.\n\
\n(press the left button to continue)", height = 0.05, rgb=(-1,-1,-1))

#set up instructions and clock (so you can time stamp duration or trials, RT etc..)
instrTxt2 = visual.TextStim(myWin,text="Before each part of the task begins, you will be informed what type of stimuli you will have to attend to by a cue in red (WORD, PICTURE or BOX).\n\
\nPlease give equal importance to SPEED and ACCURACY when completing this task. We would like you to respond as FAST as possible while maintaining a high \
level of ACCURACY.\n\
\nIf you have any questions, please ask the researcher before we start.\n\
\nWhen you are ready to begin the task, please press the left button.", height = 0.05, rgb=(-1,-1,-1))

readyTxt = visual.TextStim(myWin, text = 'The experiment will start shortly.', rgb=(-1,-1,-1))
finishTxt = visual.TextStim(myWin, text = 'End of Experiment!', rgb=(-1,-1,-1))

######### Set up constant variables outside of loop ############

# read in csv file with conditions on 
dataFile = open('StimList.csv', 'rb')
reader = csv.reader(dataFile, delimiter = ',')

#read in first line of the csv file and assign this to the variable header
header = dataFile.readline() 

#strip the header to remove \n from the end and split this line into as many entries as there are columns in the header file (i.e., into each of the columns headers)
hdr = header.strip().split(';')
lines = dataFile.readlines() #assign all other information into the variable lines
# create an empty list in which we can append items from the csv file into
go_words = []
nogo_words = []
go_box = []
nogo_box = []
go_img = []
nogo_img = []
scrambled_word = []
scrambled_pic = []
for line in lines: # read in row by row from csv file 
    data = line.strip().split(',')
    if data[0] != '':
        item1 = data[0] # filename of go word i.e., a string of words denoting my stimulus trials - in the first column of my csv file
        go_words.append(item1)
    if data[1] != '':
        item2 = data[1] # filename of nogo word
        nogo_words.append(item2)
    Block = data[2]
    Condition = data[3]
    if data[4] != '':
        item3 = (data[4])
        go_box.append(item3)
        nogo_box.append(item3)
    if data[5] != '':
        item4 = (data[5])
        go_img.append(str(os.getcwd())+item4)
    if data[6] != '':
        item5 = (str(os.getcwd())+data[6])
        nogo_img.append(item5)
    if data[7] != '':
        item6 = (str(os.getcwd())+data[7])
        scrambled_word.append(item6)
    if data[8] != '':
        item7 = (str(os.getcwd())+data[8])
        scrambled_pic.append(item7)

    
#List of numbers we can select from to determine number of consecutive go trials before a no go 
consecutive_gotrials = [2,3,4,5,6,7,8]
#length of jitter options in seconds for item and fixation
jitter_item = [0.75,1,1.25]
jitter_fixation = [0.5,0.75,1]
diffs = ['e','h']
#Participant ID
Part_ID = info['Subject']
#create a fixation cross
fixation = visual.TextStim(myWin,text='+',rgb=(-1,-1,-1))

######################################Experiment begins##############################################################

if In_scanner:
    import ynicstim.parallel_compat
    import ynicstim.trigger
    
    port = '/dev/parport0'
    p = ynicstim.parallel_compat.getParallelPort(port)
    ts = ynicstim.trigger.ParallelInterruptTriggerSource(port=p)
    trig_collector = ynicstim.trigger.TriggerCollector(triggersource=ts, slicespervol=slices_per_vol)
else:
    trig_collector = None

myClock = core.Clock()

# Presents a ready screen and waits for participant to press enter
instrTxt1.draw()
myWin.flip()
event.waitKeys(keyList=['space','return'])
#present instructions screen
instrTxt2.draw()
myWin.flip()
event.waitKeys(keyList=['space','return'])
myWin.flip()

# Start being ready to get triggers
if trig_collector:
    trig_collector.start()

readyTxt.draw()
myWin.flip()
event.waitKeys(keyList=['return'])

print 'got here'

if trig_collector:
    trig_collector.waitForVolume(5)
else:
    event.waitKeys(keyList=['return'])
    
#set up a clock from which we can getTime() to measure length of experiment and trials
myClock = core.Clock()

####### EXPERIMENTAL LOOP #################
### THIS IS WHERE DATA COLLECTION OCCURS ########

###LOOP 1. TEXT###
def Block_A(thisrun):
    global go_words
    random.shuffle(go_words)
    global nogo_words
    random.shuffle(nogo_words)
    global go_box
    global nogo_box
    global Part_ID
    #List of numbers we can select from to determine number of consecutive go trials before a no go 
    consecutive_gotrials = [1,2,3,4,5,6]
    #length of jitter options in seconds for item and fixation
    jitter_item = [0.75,1,1.25]
    jitter_fixation = [0.5,0.75,1]
    #create a fixation cross
    fixation = visual.TextStim(myWin,text='+',rgb=(-1,-1,-1))
    #SPLIT THE MINIBLOCKS HERE
    if thisrun == 1:
        slants = ['e', 'h']
    elif thisrun == 2:
        slants = ['h', 'e']

    #Cue block 1
    Cue1 = visual.TextStim(myWin,text="TEXT",
                                units = 'norm', height = 0.3, pos = (0, 0), alignVert='center', rgb=(1,-1,-1))
    Cue1.draw()
    myWin.flip()
    #This will wait for 3 seconds
    core.wait(2)
    Cue1a = visual.TextStim(myWin,text="Remember: \n\
\nPress the LEFT BUTTON if it's an OBJECT.\n\
\nDON'T PRESS anything if it's an ANIMAL.",
height = 0.1, rgb=(-1,-1,-1))
    Cue1a.draw()
    myWin.flip()
    #This will wait for 3 seconds
    core.wait(5)
    for i in slants:
        diff = i
        print 'difficulty', diff
        # Number of go trials in the block
        remaining_trials = 50
        # Keeping a track of how many trials we have completed 
        while remaining_trials > 8:
            if len(consecutive_gotrials) == 0:
                consecutive_gotrials = [1,2,3,4,5,6]
            random_gotrials = np.random.choice(consecutive_gotrials, 1, replace=False)
            # As the above line returns a one-value list, we need to select that value so that we have an int to manipulate (this is important for the next line)
            number_gotrials = random_gotrials[0]
            # select the int number_gotrials from our word list pool - this does not sample without replacement so later we will remove these items from the list to ensure no items are repeated
            rand_items = np.random.choice(go_words, number_gotrials,replace=False)
            # Then after a random number of go trials we will present a nogo item        
            nogo_item = np.random.choice(nogo_words, 1, replace=False) 
            #-I made this, trying to choose one of the three box conditions in the xlsx file at random, with replacement.
            if diff == 'e':
                cond = 'words easy'
            elif diff == 'h':
                cond = 'words hard'

            # Now we can go through the list line by line and call the stimuli in

        # Start consecutive_gotrials
            for i in range(0, len(rand_items)):
                   # Present item 
                   #Decide Box
                    cointoss = np.random.choice((1, 2), 1)
                    # Draw fixation cross
                    fixation.draw()
                    rand_jitter_fix = random.choice(jitter_fixation)
                    myWin.flip()
                    core.wait(rand_jitter_fix)
                    rt_clock = core.Clock()
                    
                    # Prepare go stimulus each iteration
                    go_stimulus = visual.TextStim(myWin, 
                                        units='norm',height = 0.1,
                                        pos=(0, 0), text=rand_items[i],
                                        font=sans, 
                                        alignHoriz = 'center',alignVert='center',
                                        rgb=(-1,-1,-1))

                    if diff == 'e':
                        if cointoss[0] == 1:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif diff == 'h':
                        if cointoss[0] == 1:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)


                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                     
                    while contTrial and rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        corrAns = 'left'
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            RT = rt_clock.getTime()
                            isCorrect = int(thisResp == corrAns)
                            if isCorrect == 1:
                                isCorrect = True
                            else:
                                isCorrect = False 
                    while rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()


                    #Write data into logfile
                    boxtype = 'unknown'
                    itemname = rand_items[i]
                    if cointoss[0] == 1:
                        boxtype = 'square'
                    elif cointoss[0] == 2 and diff =='e':
                        boxtype = 'easy'
                    elif cointoss[0] == 2 and diff == 'h':
                        boxtype = 'hard'
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block A', cond, 'GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1

        #Start No Go Trial
            #Decide Box
            cointoss = np.random.choice((1, 2), 1)

            # Draw fixation point
            fixation.draw()
            rand_jitter_fix = random.choice(jitter_fixation)
            myWin.flip()
            core.wait(rand_jitter_fix)
            rt_clock = core.Clock()
            
            # Prepare and draw the stimulus
            for line_nogo in nogo_item:
                    nogo_stimulus = visual.TextStim(myWin, 
                                        units='norm',height = 0.1,
                                        pos=(0, 0), text=line_nogo,
                                        font=sans, 
                                        alignHoriz = 'center',alignVert='center',
                                        rgb=(-1,-1,-1))

                    if diff == 'e':
                        if cointoss[0] == 1:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif diff == 'h':
                        if cointoss[0] == 1:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)

                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                    while contTrial and rt_clock.getTime() < durStim:
                        nogo_stimulusv.draw()
                        nogo_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            isCorrect = False
                            RT = rt_clock.getTime()
                        else:
                            isCorrect = True
                                                         
                    while rt_clock.getTime() < durStim:
                        nogo_stimulusv.draw()
                        nogo_stimulus.draw()
                        myWin.flip()

                    #Write data into logfile
                    boxtype = 'unknown'
                    itemname = line_nogo
                    if cointoss[0] == 1:
                        boxtype = 'square'
                    elif cointoss[0] == 2 and diff =='e':
                        boxtype = 'easy'
                    elif cointoss[0] == 2 and diff == 'h':
                        boxtype = 'hard'
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block A', cond, 'NO GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1


            go_words = [ x for x  in go_words if x not in rand_items]
            nogo_words = [ x for x  in nogo_words if x not in nogo_item]
            consecutive_gotrials = [ x for x in consecutive_gotrials if x not in random_gotrials]

        # If the while statement is no longer true then do the following
        else:
            #select the items left in go_items. We use len(go_items) as this value will change on each block
                # When there's less than 8 trials, we choose a random number to complete +4
            print 'last run with %i remaining trials' %(remaining_trials)
            random.shuffle(go_words)
            rand_items = np.random.choice(go_words, (remaining_trials + random.randint(1, 3)), replace=False)
            if diff == 'e':
                cond = 'words easy'
            elif diff == 'h':
                cond = 'words hard'


            for i in range(0, len(rand_items)):
                #Decide Box
                cointoss = np.random.choice((1, 2), 1)
                
                # Draw fixation cross
                fixation.draw()
                rand_jitter_fix = random.choice(jitter_fixation)
                myWin.flip()
                core.wait(rand_jitter_fix)
                
                #prepare consecutive go trials
                go_stimulus = visual.TextStim(myWin, 
                                    units='norm',height = 0.1,
                                    pos=(0, 0), text=rand_items[i],
                                    font=sans, 
                                    alignHoriz = 'center',alignVert='center',
                                    rgb=(-1,-1,-1))

                if diff == 'e':
                    if cointoss[0] == 1:
                        go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif cointoss[0] == 2:
                        go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                elif diff == 'h':
                    if cointoss[0] == 1:
                        go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif cointoss[0] == 2:
                        go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)


                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                     
                    while contTrial and rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        corrAns = 'left'
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            RT = rt_clock.getTime()
                            isCorrect = int(thisResp == corrAns)
                            if isCorrect == 1:
                                isCorrect = True
                            else:
                                isCorrect = False 
                    while rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                                
                    #Write data into logfile
                    boxtype = 'unknown'
                    itemname = rand_items[i]
                    if cointoss[0] == 1:
                        boxtype = 'square'
                    elif cointoss[0] == 2 and diff =='e':
                        boxtype = 'easy'
                    elif cointoss[0] == 2 and diff == 'h':
                        boxtype = 'hard'
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block A', cond, 'GO', itemname, boxtype, isCorrect, thisResp, RT, Onset,durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1
                
                
                go_words = [ x for x  in go_words if x not in rand_items]

    # Rest screen goes here

    rest_screen = visual.TextStim(myWin, 
                        units='norm',
                        pos=(0, 0), text="5 second rest. The experiment will begin shortly",
                        font=sans, 
                        alignHoriz = 'center',alignVert='center',
                        rgb=(-1,-1,-1))
    rest_screen.draw()
    myWin.flip() 
    core.wait(5)




###LOOP 2. IMAGE###
def Block_B(thisrun):
    global go_img
    random.shuffle(go_img)
    global nogo_img
    random.shuffle(nogo_img)
    global go_words
    random.shuffle(go_words)
    global nogo_words
    random.shuffle(nogo_words)
    global go_box
    global nogo_box
    global Part_ID
    #List of numbers we can select from to determine number of consecutive go trials before a no go 
    consecutive_gotrials = [1,2,3,4,5,6]
    #length of jitter options in seconds for item and fixation
    jitter_item = [0.75,1,1.25]
    jitter_fixation = [0.5,0.75,1]
    #create a fixation cross
    fixation = visual.TextStim(myWin,text='+',rgb=(-1,-1,-1))
    #SPLIT THE MINIBLOCKS HERE
    if thisrun == 1:
        slants = ['e', 'h']
    elif thisrun == 2:
        slants = ['h', 'e']

    #Cue block 2
    Cue2 = visual.TextStim(myWin,text="PICTURE",
                                units = 'norm', height = 0.3, pos = (0, 0), alignVert='center', rgb=(1,-1,-1))
    Cue2.draw()
    myWin.flip()
    #This will wait for 3 seconds
    core.wait(2)
    Cue2a = visual.TextStim(myWin,text="Remember: \n\
\nPress the LEFT BUTTON if it's an OBJECT.\n\
\nDON'T PRESS anything if it's an ANIMAL.",
height = 0.1, rgb=(-1,-1,-1))
    Cue2a.draw()
    myWin.flip()
    #This will wait for 3 seconds
    core.wait(5)
    for i in slants:
        diff = i
        print 'difficulty', diff
        # Number of go trials in the block
        remaining_trials = 50
        # Keeping a track of how many trials we have completed 
        while remaining_trials > 8:
            if len(consecutive_gotrials) == 0:
                consecutive_gotrials = [1,2,3,4,5,6]
            random_gotrials = np.random.choice(consecutive_gotrials, 1, replace=False)
            # As the above line returns a one-value list, we need to select that value so that we have an int to manipulate (this is important for the next line)
            number_gotrials = random_gotrials[0]
            # select the int number_gotrials from our word list pool - this does not sample without replacement so later we will remove these items from the list to ensure no items are repeated
            rand_items = np.random.choice(go_img, number_gotrials,replace=False)
            # Then after a random number of go trials we will present a nogo item
            nogo_item = np.random.choice(nogo_img, 1, replace=False)
            # This should call the Square box, and store it n times where n is the number of go trials this loop
            if diff == 'e':
                cond = 'image easy'
            elif diff == 'h':
                cond = 'image hard'

            # Now we can go through the list line by line and call the stimuli in

        #Start Consecutive Go Trials

            for i in range(0, len(rand_items)):
                    #Decide Box
                    cointoss = np.random.choice((1, 2), 1)

                    # Draw fixation cross
                    fixation.draw()
                    rand_jitter_fix = random.choice(jitter_fixation)
                    myWin.flip()
                    core.wait(rand_jitter_fix)
                    rt_clock = core.Clock()
                    # Prepare each stimuli each iteration
                    go_stimulus = visual.ImageStim(myWin, size=0.44, units='norm',
                                        pos=(0, 0), image=rand_items[i])

                    if diff == 'e':
                        if cointoss[0] == 1:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif diff == 'h':
                        if cointoss[0] == 1:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)

                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                     
                    while contTrial and rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        corrAns = 'left'
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            RT = rt_clock.getTime()
                            isCorrect = int(thisResp == corrAns)
                            if isCorrect == 1:
                                isCorrect = True
                            else:
                                isCorrect = False 
                    while rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        
                    #Write data into logfile
                    boxtype = 'unknown'
                    itemid = rand_items[i].split("\\")
                    itemname = itemid[-1][:-4]
                    if cointoss[0] == 1:
                        boxtype = 'square'
                    elif cointoss[0] == 2 and diff =='e':
                        boxtype = 'easy'
                    elif cointoss[0] == 2 and diff == 'h':
                        boxtype = 'hard'
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block B', cond, 'GO', itemname, boxtype, isCorrect, thisResp, RT, Onset,durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1


        #Start No Go Trial
            #Decide Box
            cointoss = np.random.choice((1, 2), 1)

            # Draw fixation point
            fixation.draw()
            rand_jitter_fix = random.choice(jitter_fixation)
            myWin.flip()
            core.wait(rand_jitter_fix)
            rt_clock = core.Clock()
            
            # Prepare and draw the stimulus
            for line_nogo in nogo_item:
                    nogo_stimulus = visual.ImageStim(myWin, size=0.44, units='norm',
                                        pos=(0, 0), image=line_nogo) 

                    if diff == 'e':
                        if cointoss[0] == 1:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif diff == 'h':
                        if cointoss[0] == 1:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            nogo_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)


                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                    while contTrial and rt_clock.getTime() < durStim:
                        nogo_stimulusv.draw()
                        nogo_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            isCorrect = False
                            RT = rt_clock.getTime()
                        else:
                            isCorrect = True
                                                         
                    while rt_clock.getTime() < durStim:
                        nogo_stimulusv.draw()
                        nogo_stimulus.draw()
                        myWin.flip()

                    #Write data into logfile
                    boxtype = 'unknown'
                    itemid = nogo_item[0].split("\\")
                    itemname = itemid[-1][:-4]
                    if cointoss[0] == 1:
                        boxtype = 'square'
                    elif cointoss[0] == 2 and diff =='e':
                        boxtype = 'easy'
                    elif cointoss[0] == 2 and diff == 'h':
                        boxtype = 'hard'
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block B', cond, 'NO GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1

            #This removes the items from the list that you have used (true sampling without replacement) 
            go_img = [ x for x  in go_img if x not in rand_items]
            nogo_img = [ x for x  in nogo_img if x not in nogo_item]
            consecutive_gotrials = [ x for x in consecutive_gotrials if x not in random_gotrials]



        # If the while statement is no longer true then do the following
        else: 
            # When there's less than 8 trials, we choose a random number to complete +4
            print 'last run with %i remaining trials' %(remaining_trials)
            random.shuffle(go_img)
            rand_items = np.random.choice(go_img, (remaining_trials + random.randint(1, 3)),replace=False)
            if diff == 'e':
                cond = 'image easy'
            elif diff == 'h':
                cond = 'image hard'



        #Start the last Go trials sequence to reach n 100
            for i in range(0, len(rand_items)):
                    #Decide Box
                    cointoss = np.random.choice((1, 2), 1)

                    # Draw fixation cross
                    fixation.draw()
                    rand_jitter_fix = random.choice(jitter_fixation)
                    myWin.flip()
                    core.wait(rand_jitter_fix)
                    
                    # Prepare and draw each stimuli each iteration
                    go_stimulus = visual.ImageStim(myWin, size=0.44, units='norm',
                                        pos=(0, 0), image=go_img[i])

                    if diff == 'e':
                        if cointoss[0] == 1:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif diff == 'h':
                        if cointoss[0] == 1:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                        elif cointoss[0] == 2:
                            go_stimulusv = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)


                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                     
                    while contTrial and rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        corrAns = 'left'
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            RT = rt_clock.getTime()
                            isCorrect = int(thisResp == corrAns)
                            if isCorrect == 1:
                                isCorrect = True
                            else:
                                isCorrect = False 
                    while rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()

                    #Write data into logfile
                    itemid = go_img[i].split("\\")
                    itemname = itemid[-1][:-4]
                    if cointoss[0] == 1:
                        boxtype = 'square'
                    elif cointoss[0] == 2 and diff =='e':
                        boxtype = 'easy'
                    elif cointoss[0] == 2 and diff == 'h':
                        boxtype = 'hard'
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block B', cond, 'GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1

            go_img = [ x for x  in go_img if x not in rand_items]


    # Rest screen goes here

    rest_screen = visual.TextStim(myWin, 
                        units='norm',
                        pos=(0, 0), text="5 second rest. The experiment will begin shortly",
                        font=sans, 
                        alignHoriz = 'center',alignVert='center',
                        rgb=(-1,-1,-1))
    rest_screen.draw()
    myWin.flip() 
    core.wait(5)



###BLOCK C. SCRAMBLED
def Block_C(thisrun):
    global go_words
    global nogo_words
    global go_box
    global nogo_box
    global scrambled_word
    global scrambled_pic
    global Part_ID

    #List of numbers we can select from to determine number of consecutive go trials before a no go 
    consecutive_gotrials = [1,2,3,4,5,6]
    #length of jitter options in seconds for item and fixation
    jitter_item = [0.75,1,1.25]
    jitter_fixation = [0.5,0.75,1]
    #create a fixation cross
    fixation = visual.TextStim(myWin,text='+',rgb=(-1,-1,-1))
    scrambled_img = []
    #SPLIT THE MINIBLOCKS HERE
    if thisrun == 1:
        slants = ['e', 'h']
    elif thisrun == 2:
        slants = ['h', 'e']

    #Cue block 3
    Cue3 = visual.TextStim(myWin,text="BOX",
                                units = 'norm', height = 0.3, pos = (0, 0), alignVert='center', rgb=(1,-1,-1))
    Cue3.draw()
    myWin.flip()
    #This will wait for 3 seconds
    core.wait(2)
    Cue3a = visual.TextStim(myWin,text="Remember: \n\
\nPress the LEFT BUTTON if the BOX ISN'T VERY SLANTED.\n\
\nDON'T PRESS anything if THE BOX IS MORE SLANTED.",
height = 0.1, rgb=(-1,-1,-1))
    Cue3a.draw()
    myWin.flip()
    #This will wait for 3 seconds
    core.wait(5)

    for i in slants:
        diff = i
        print 'difficulty', diff
        if thisrun == 1 and diff == 'e':
            cond = 'scrambled words easy'
            for i in scrambled_word:
                scrambled_img.append(i)
        elif thisrun == 1 and diff == 'h':
            cond = 'scrambled pics hard'
            for i in scrambled_pic:
                scrambled_img.append(i)
        elif thisrun == 2 and diff == 'e':
            cond = 'scrambled pics easy'
            for i in scrambled_pic:
                scrambled_img.append(i)
        elif thisrun == 2 and diff == 'h':
            cond = 'scrambled words hard'
            for i in scrambled_word:
                scrambled_img.append(i)
        # Number of go trials in the block
        remaining_trials = 50

        # Keeping a track of how many trials we have completed 
        random.shuffle(scrambled_img)
        while remaining_trials > 8:
            if len(consecutive_gotrials) == 0:
                consecutive_gotrials = [1,2,3,4,5,6]
            random_gotrials = np.random.choice(consecutive_gotrials, 1, replace=False)
            # As the above line returns a one-value list, we need to select that value so that we have an int to manipulate (this is important for the next line)
            number_gotrials = random_gotrials[0]
            #-I made this, trying to choose one of the three box conditions in the xlsx file at random, with replacement.
            gobox_item = np.random.choice(scrambled_img, number_gotrials, replace=False)
            nogobox_item = np.random.choice(scrambled_img, 1, replace=False)


            # Now we can go through the list line by line and call the stimuli in

        #Start Consecutive Go Trials
            for i in range(0, len(gobox_item)):
                    # Draw fixation cross
                    fixation.draw()
                    rand_jitter_fix = random.choice(jitter_fixation)
                    myWin.flip()
                    core.wait(rand_jitter_fix)
                    rt_clock = core.Clock()
                    # Prepare and draw each stimuli each iteration
                    go_stimulus = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    go_stimulusv = visual.ImageStim(myWin, size=0.44,
                                                image=gobox_item[i],
                                                pos=(0, 0))
                   
                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                     
                    while contTrial and rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        corrAns = 'left'
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            RT = rt_clock.getTime()
                            isCorrect = int(thisResp == corrAns)
                            if isCorrect == 1:
                                isCorrect = True
                            else:
                                isCorrect = False 
                    while rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()


                    #Write data into logfile
                    boxtype = 'square'
                    itemid = gobox_item[i].split("\\")
                    itemname = itemid[-1][:-4]
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block C', cond, 'GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1

        #Start No Go Trial
            # Draw fixation point
            fixation.draw()
            rand_jitter_fix = random.choice(jitter_fixation)
            myWin.flip()
            core.wait(rand_jitter_fix)
            rt_clock = core.Clock()
            
            # Prepare and draw the stimulus
            for line_nogo in nogobox_item:
                    if diff == 'e':
                        nogo_stimulus = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.22, 0.5), (0.78, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.12, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    elif diff == 'h':
                        nogo_stimulus = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.31, 0.5), (0.69, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                closeShape=True, pos=(-0.09, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    nogo_stimulusv = visual.ImageStim(myWin, size=0.44,
                                        pos=(0, 0), image=nogobox_item[0])
                                        
                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                    while contTrial and rt_clock.getTime() < durStim:
                        nogo_stimulusv.draw()
                        nogo_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            isCorrect = False
                            RT = rt_clock.getTime()
                        else:
                            isCorrect = True
                                                         
                    while rt_clock.getTime() < durStim:
                        nogo_stimulusv.draw()
                        nogo_stimulus.draw()
                        myWin.flip()

            #Write data into logfile
                    if diff == 'e':
                        boxtype = 'easy'
                    elif diff == 'h':
                        boxtype = 'hard'
                    itemid = nogobox_item[0].split("\\")
                    itemname = itemid[-1][:-4]
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block C', cond, 'NO GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1
            

            #This removes the items from the list that you have used (true sampling without replacement) 
            consecutive_gotrials = [ x for x in consecutive_gotrials if x not in random_gotrials]



        # If the while statement is no longer true then do the following
        else: 
            # When there's less than 8 trials, we choose a random number to complete +4
            print 'last run with %i remaining trials' %(remaining_trials)
            random.shuffle(scrambled_img)
            gobox_item = np.random.choice(scrambled_img, (remaining_trials + random.randint(1, 3)), replace=False)

        #Start the last Go trials sequence to reach n 100
            for i in range(0, len(gobox_item)):
                    # Draw fixation cross
                    fixation.draw()
                    rand_jitter_fix = random.choice(jitter_fixation)
                    myWin.flip()
                    core.wait(rand_jitter_fix)
                    rt_clock = core.Clock()
                    # Prepare and draw each stimuli each iteration
                    go_stimulus = visual.ShapeStim(myWin, units='', lineWidth=4, lineColor='black', lineColorSpace='rgb', fillColor=None, fillColorSpace='rgb', vertices=((-0.41, 0.5), (0.59, 0.5), (0.5, -0.5), (-0.5, -0.5)), \
                                                                    closeShape=True, pos=(-0.06, 0), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=0, interpolate=True, name=None, autoLog=None, autoDraw=False)
                    go_stimulusv = visual.ImageStim(myWin, size=0.44,
                                                image=gobox_item[i],
                                                pos=(0, 0))
                    
                    durStim = random.choice(jitter_item)
                    contTrial=True
                    event.clearEvents() #start each trial by clearing event buffer to prevent any previous keys interfering with the current trial
                    rt_clock.reset()
                    Onset = myClock.getTime()
                     
                    while contTrial and rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()
                        thisResp, thisRT = get_response(input_method, resp_device, myClock)
                        RT = 0
                        corrAns = 'left'
                        isCorrect = 'noResponse'
                        if thisResp is not None:
                            contTrial = False
                            RT = rt_clock.getTime()
                            isCorrect = int(thisResp == corrAns)
                            if isCorrect == 1:
                                isCorrect = True
                            else:
                                isCorrect = False 
                    while rt_clock.getTime() < durStim:
                        go_stimulusv.draw()
                        go_stimulus.draw()
                        myWin.flip()

                    #Write data into logfile
                    boxtype = 'square'
                    itemid = gobox_item[i].split("\\")
                    itemname = itemid[-1][:-4]
                    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%f,%f,%f\n' %(Part_ID,'Block C', cond, 'GO', itemname, boxtype, isCorrect, thisResp, RT, Onset, durStim))
                    f.flush()
                    remaining_trials = remaining_trials - 1

        scrambled_img = []

    # Rest screen goes here

    rest_screen = visual.TextStim(myWin, 
                        units='norm',
                        pos=(0, 0), text="5 second rest. The experiment will begin shortly",
                        font=sans, 
                        alignHoriz = 'center',alignVert='center',
                        rgb=(-1,-1,-1))
    rest_screen.draw()
    myWin.flip() 
    core.wait(5)

###CALL THE ORDER###
#DEBUGGER
#testing (uncomment as needed)
#diff = 'e'
#Block_A(diff)
#Block_B(diff)
#Block_C(diff)


thisrun = 1
Block_B(thisrun)
Block_C(thisrun)
Block_A(thisrun)
#thisrun = 2
#Block_A(thisrun)
#Block_C(thisrun)
#Block_B(thisrun)


f.write('Done at %f'%(myClock.getTime()))

############################################End Experiment###############################################################
# If in fMRI mode, store the triggers
if trig_collector:
    trig_collector.endCollection()
    v_t = trig_collector.getVolumeTimings(myClock)

    # Create a file which has the fMRI timings in
    for x in range(len(v_t)):
        fmri_log.write('%d,%.3f\n' % (x, v_t[x]))

finishTxt.draw()
myWin.flip()
fin_time=myClock.getTime()
print(fin_time)
event.waitKeys()
f.close()
fmri_log.close()
