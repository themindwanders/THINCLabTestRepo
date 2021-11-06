# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 10:36:57 2018

@author: xw1365
"""

"""
%%% This function is for running an arithmetic (addition) task while scanning in fMRI                      %%% 
%%% Subject's task: press the button (left / right) corresponding to the correct answer 
%%% of each expression %%%
% subjID: subject id
% runNum: run number (1 / 2)
% theSpeed: 1 = normal (3s), 2 = slow (4s)
% IPS should be: normal speed, 158; slow speed, 198

Adapted from Eve's arithmeticTaskNew.mat

This experiment has two runs. The difference is the order.
Each run has 16 blocks, each block has 5 trials, 5H, 5E, 5E, 5H. 
After every block, there is a long fixation (15s).
The final fixation is 16s.

Run1 : 5E, 5H, 5H, 5E.......
Run2 : 5H, 5E, 5E, 5H.......

Each trial: expression 1.45s, choice 1.45s, blank screen 0.1s. One trial is 3s.

Fixa Block1 Fixa  B2    Fixa   B3   Fixa   B4   Fixa
15   60     15    60    15     60    15    60   16    = 316s = 5min 16s (one run)

Block1 = 5H, 5E, 5E, 5H

"""

from psychopy import visual, core, monitors, event, sound, gui, logging
from datetime import datetime
from random import shuffle
import os
import time
import csv
import sys, os, errno # to get file system encoding (used in setDir())
import numpy as np
import random
from collections import OrderedDict

def mathTask(time, win):
    ### Initialize variables

    # file related

    expName = 'MathLocaExp'
    stimuli = 'math_stimuli'
    data_folder = 'data' + '_' +  expName
    instruct_figure = 'math_instr(1.2).png'
    # trigger_figure = 'trigger.png'
    # ready_figure = 'ready.png'

    # experiment details related
    num_of_trials = 80
    num_of_fix = 5
    expr_time = 1.45 # formal experiment, it is 1.45
    choi_time = 1.45  # formal experiment, it is 1.45
    blank_time = 0.1   # display a blank screen
    timelimit_deci = 1.45 # equal to the choi_time 1.45 (check)
    trial_time = expr_time + choi_time + blank_time  # each trial is 3s

    pretrialFixDur = 15.00;  # in seconds previous four fixation is 15s
    posttrialFixDur = 16.00; # in seconds the final fixation is 16s

    instru_key     = ['return','escape']
    choie_key_list = ['1','2','escape']  # 1 == left, 2 == right

    # window related
    # windows
    # assign the monitor name
    monitor_name = 'HP ProOne 600'

    # window size = x, y
    # win_size_x = 1920
    # win_size_y = 1920

    # # window background color
    # win_bg_col   = (-1,-1,-1)
    # win_text_col = (1.0,1.0,1.0)  # text color

    # instruction, position height
    word_pos = (0,0)
    text_h     = 120
    # fixa_h     = 200
    instru_pos = (0,0)
    # instru_h =100
    choice_right_pos =(-0.1,0)
    choice_left_pos =(0.1,0)
    # 
    trigger_instru = 'experiment starts soon'
    ready_instru = 'Do not move head'
    ### define functions

    # get the current directory of this script - correct
    def get_pwd():
        global curr_dic
        curr_dic = os.path.dirname(sys.argv[0])  # U:/task_fMRI_Experiment/exp_March
        return curr_dic

    # make a folder in the current directory used to store data  - correct
    def makedir(folder_name):
        os.chdir(curr_dic)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def shutdown ():
        win.close()
        core.quit()

    # get the participants info, initialize the screen and create a data file for this subject
    def info_gui(expName):
        # Set up a dictionary in which we can store our experiment details
        expInfo={}
        expInfo['expname'] =expName
        # Create a string version of the current year/month/day hour/minute
        expInfo['expdate']=datetime.now().strftime('%Y%m%d_%H%M')
        expInfo['subjID']=['1','2']
        # expInfo['subjName']=''
        # expInfo['run']=''
        
        # Set up our input dialog
        # Use the 'fixed' argument to stop the user changing the 'expname' parameter
        # Use the 'order' argument to set the order in which to display the fields
        dlg = gui.DlgFromDict(expInfo,title='input data', fixed = ['expname','expdate'],order =['expname','expdate','subjID'])
        # dlg = gui.DlgFromDict(expInfo,title='input data', fixed = ['expname','expdate'],order =['expname','expdate','subjID','subjName','run'])

        if not dlg.OK:
            print ('User cancelled the experiment')
            core.quit()
    
    # creates a file with a name that is absolute path + info collected from GUI
        # filename = data_folder + os.sep + '%s_%s_%s_%s.csv' %(expInfo['subjID'], expInfo['subjName'], expInfo['expdate'],expInfo['run'])
        # filename_fixa = data_folder + os.sep + '%s_%s_%s_%s_fixa.csv' %(expInfo['subjID'], expInfo['subjName'], expInfo['expdate'],expInfo['run'])
        filename = data_folder + os.sep + '%s_%s_.csv' %(expInfo['subjID'], expInfo['expdate'])
        filename_fixa = data_folder + os.sep + '%s_%s_fixa.csv' %(expInfo['subjID'], expInfo['expdate'])
        
        stimuli_file = stimuli+expInfo['subjID']+'.csv'
        return expInfo, filename,stimuli_file,filename_fixa
    # to avoid overwriting the data. Check whether the file exists, if not, create a new one and write the header.
    # Otherwise, rename it - repeat_n
    # correct
    def write_file_not_exist(filename):
        repeat_n = 1
        while True:
            if not os.path.isfile(filename):
                f = open(filename,'w')
            # f.write(header)F
                break
            else:
                filename = data_folder + os.sep + '%s_%s_%s_repeat_%s.csv' %(expInfo['subjID'], expInfo['expdate'],str(repeat_n))
                repeat_n = repeat_n +  1

    # Open a csv file, read through from the first row   # correct
    def load_conditions_dict(conditionfile):

    #load each row as a dictionary with the headers as the keys
    #save the headers in its original order for data saving

    # csv.DictReader(f,fieldnames = None): create an object that operates like a regular reader 
    # but maps the information in each row to an OrderedDict whose keys
    # are given by the optional fieldnames parameter.

        with open(conditionfile) as csvfile:
            reader = csv.DictReader(csvfile)
            trials = []

            for row in reader:
                trials.append(row)
        
        # save field names as a list in order
            fieldnames = reader.fieldnames  # filenames is the first row, which used as keys of trials

        return trials, fieldnames   # trial is a list, each element is a key-value pair. Key is the 
                                    # header of that column and value is the corresponding value

    # Create the log file to store the data of the experiment 
    # create the header

                
    def write_header(filename, header):
        with open (filename,'a') as csvfile:
            fieldnames = header
            data_file = csv.DictWriter(csvfile,fieldnames=fieldnames,lineterminator ='\n')
            data_file.writeheader()
            
    #write each trial
    def write_trial(filename,header,trial):
        with open (filename,'a') as csvfile:
            fieldnames = header
            data_file = csv.DictWriter(csvfile,fieldnames=fieldnames,lineterminator ='\n')
            data_file.writerow(trial)
            
    # set up the window
    # fullscr: better timing can be achieved in full-screen mode
    # allowGUI: if set to False, window will be drawn with no frame and no buttons to close etc...

    def set_up_window(window=win): 
        mon = monitors.Monitor(monitor_name)
        mon.setDistance (114)
        win = window
        win.mouseVisible = False
        return win

    # read the content in the csv or text file
    def read_cont(filename):
        f = open(filename,'r')
        return f

    # prepare the content on the screen
    # removed height from function
    def prep_cont(line, pos):
        line_text = visual.TextStim(win, line, color='black', pos=pos, bold=True)
        return line_text

    # display the content on the screen
    def disp_instr_cont(line):
        line.draw()
        win.flip()
        keys = event.waitKeys(keyList =['return','escape'])
        if keys[0][0]=='escape':
            shutdown()
    # display instruction figure on the screen
    def instruct(path,instruct_figure):
        """
        path is where the instruct figure stored
        instruct_figure is the name of instruct_figure
        """
        imstim = visual.ImageStim(win,image = os.path.join(path,instruct_figure),pos = instru_pos)
        imstim.draw()
        event.clearEvents()
        instru_onset = win.flip()
        keys = event.waitKeys(keyList =['return','escape'],timeStamped = True)
        if keys[0][0]=='escape':
            shutdown()

    def trigger_exp(path,trigger_figure):

        
        #trigger = prep_cont(trigger_instru, instru_pos,instru_h)
        trigger = visual.ImageStim(win,image = os.path.join(path,trigger_figure),pos = instru_pos)
        trigger.draw()
        win.flip()
        
        
    def ready(path,ready_figure):

        # ready_dis = prep_cont(ready_instru,instru_pos,instru_h)
        ready_dis=visual.ImageStim(win,image = os.path.join(path,ready_figure),pos = instru_pos)
        ready_dis.draw()
        ready_onset = win.flip()
        return ready_onset

    def end_exp():

        trigger = prep_cont('End of Experiment',instru_pos )
        trigger.draw()
        end_onset = win.flip()
        keys = event.waitKeys(keyList =['return'],timeStamped = True)
        print ('end of experiment:',end_onset)
        return end_onset
        
        
    # display each trial on the screen at the appropriate time
    def run_stimuli(stimuli_file):
        # read the stimuli  # re-define, not use numbers, but use keywords
            
        all_trials, headers = load_conditions_dict(conditionfile=stimuli_file)
        headers += ['i_trial_onset','trial_onset','choice_onset','blank_r_onset', 'RT', 'correct','KeyPress']   

        # open the result file to write the header
        
        write_header(filename,headers)
        
        # open the fixation file     
        f=open(filename_fixa,'a')
        
        # prepare fixation and blank screen for drawing
        fixa = prep_cont('+',word_pos)
        blank = prep_cont(' ',word_pos)
        
        # wait for the scanner to trigger the experiment
        # trigger_exp(curr_dic,trigger_figure)
        # event.waitKeys(keyList=['5'], timeStamped=True)
        #  remind the subjects that experiment starts soon.
    #    ready(curr_dic,ready_figure)
    #    core.wait(4)  # 2 TRs
    #    win.flip() 
    

    # write the fixation time into the fixation.csv file    
        fixa_numth = 1  
        blockfixa_onset_abs = 0
        f.write('%f,%.2f\n'% (fixa_numth, blockfixa_onset_abs))
    # draw the first long fixation and flip the window 

        fixa.draw()
        timetodraw = core.monotonicClock.getTime()
    #        
        while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
            pass
        
        run_onset = win.flip()  # this is when the real experiment starts and the run starts
        
        print ('----run_onset is : ---',run_onset)
        
    #    timetodraw = run_onset + pretrialFixDur
    #    while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
    #        pass
        
        count = 1 # initiaze count
        
        for trial in all_trials: 
            
            #''' trial is a ordered dictionary. The key is the first raw of the stimuli csv file'''
            expression = prep_cont(trial['expression'],word_pos)
            choice     = prep_cont(trial['choice'][0:4],choice_left_pos)
            choice_right = prep_cont(trial['choice'][len(trial['choice'])-4::],choice_right_pos)



            # display expression - the start of a new trial
            expression.draw()
            ideal_trial_onset = float( pretrialFixDur) +float(run_onset) + float( trial['expr_onset'])
            timetodraw = ideal_trial_onset
            while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                pass
            trial_onset = win.flip()  # when expression is displayed, this is the trial onset
            
            
            # display choice and ask subjects to press the button 1 or 2
            choice.draw()
            choice_right.draw()
            timetodraw = trial_onset + expr_time
            while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                    pass
            event.clearEvents()
            choice_onset = win.flip()
            keys = event.waitKeys(maxWait = timelimit_deci, keyList =['1','2','3','4','escape'],timeStamped = True)
            

            # If subjects do not press the key within maxwait time, RT is the timilimit and key is none and it is false
            if keys is None:
                RT = 'None'
                keypress = 'None'
                correct = 'False'

        # If subjects press the key, record which key is pressed, RT and whether it is right
            elif type(keys) is list:
                if keys[0][0]=='escape':
                    shutdown()
                
                else:
                    keypress = keys[0][0]
                    RT = keys[0][1] - choice_onset       
                    correct = (keys[0][0]==trial['correct_ans']) 
                    trial['RT']=RT
                    trial['correct'] = correct
                    trial['KeyPress'] = keypress

        
            trial['i_trial_onset'] = float( pretrialFixDur) + float( trial['expr_onset'])
            trial['trial_onset']   = trial_onset - run_onset
            trial['choice_onset']  = choice_onset - run_onset
            trial['RT'] = RT
            trial['correct'] = correct
            trial['KeyPress'] = keypress
            
            blank.draw()
            timetodraw = trial_onset + expr_time + choi_time       
            while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                pass
            blank_r_onset = win.flip()

            trial['blank_r_onset']=blank_r_onset - run_onset

        
            write_trial(filename,headers,trial)     # calls the function that writes csv output
            
    # display the long fixation after every 20 trials.
    # But at the end of all the trials, the fixation time is posttrialFixDur (16s).
    # Otherwise, it is pretrialFixDur (15s)

            if count % 20 ==0:
                fixa_numth += 1
                if count!=80:
                    fixa_time = pretrialFixDur
                else:
                    fixa_time = posttrialFixDur
                    
                fixa.draw()
                timetodraw = ideal_trial_onset + trial_time
                while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                    pass
                    
                blockfixa_onset=win.flip()
                blockfixa_onset_abs = blockfixa_onset - run_onset
                f.write('%f,%.2f\n'% (fixa_numth, blockfixa_onset_abs)) 
                
                timetodraw = ideal_trial_onset + trial_time + fixa_time
                while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                    pass
    
            count+=1 # the number-th trials that are displaying

    # -----------------------------------------------------------------------------------------------------------------------------------------------
    # call the functions defined
    # get the current directory
    curr_dic = get_pwd()

    # make a directory – data to store the generated data
    makedir(data_folder)

    # record subjects info and create a csv file with the info about subjects
    expInfo, filename, stimuli_file,filename_fixa = info_gui(expName)

    # if the data does not exist, create one, otherwise,  rename one –filename-repeat-n
    write_file_not_exist(filename)
    write_file_not_exist(filename_fixa)
    # set up the window to display the instruction
    win = set_up_window()

    # read the instruction
    #instruct()

    # generate the jitter list for the fixation and probe
    # know the number of trials
    trials, fieldnames = load_conditions_dict(stimuli_file)


    # show the instruction
    instruct(curr_dic,instruct_figure)
            
    ### use 
    # Trigger the scanner
    # displays that experiment is about to start -  waiting for dummy volumes to be acquired     
    # experimenter does not have to press 5. The scanner would be triggered in this way. 
    # This is not useful for the behaviour experiment    
    # expSoon.draw()


    # run the stimuli
    run_stimuli(stimuli_file)

    ## end of the experiment
    end_exp()
    # Lucilla would like to discard some volumes at the beginning of the scanning - Xiuyi.
    # That's why she asked her experiment to wait for 4s to start. - Xiuyi
    # Not useful for the behaviour experiment
    # core.wait(4)
    # win.flip()

    # sets a local clock that will be used to store timing information synced with the scanner

    #expClock = core.Clock()
    #
    #print (' the end of the experment: ', expClock,)
    #expClock.reset()     
    #    
        
    # Experiment()  
time = core.Clock
mathTask(time, visual.Window(size=(1280, 800),color='white', winType='pyglet')) 
