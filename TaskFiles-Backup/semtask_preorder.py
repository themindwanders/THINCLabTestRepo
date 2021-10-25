# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:47:22 2019

"""
import os
import sys
import random
from psychopy import core, event, logging, visual, data
import pandas as pd
from random import choice

from src.library import *




# get input for dictionary defining the environment & trials to run
INFO = {
    'Experiment': 'Task2019',  # compulsory: name of program, used for trial definition in ./parameter/~.csv
    'Subject': 'B',  # compulsory
    #'Subtask': ['Self', 'Other'],  # start the task with block for Self or Other
    'Environment': ['lab', 'mri'],  # mri version can be tested on a normal stimuli delivery pc
    'ESQuestion': ['ES', 'No ES'], # with or without experience sampling
    }

# MRI related settings
dummy_vol = 0
tr = 2
trigger_code = '5'

experiment_info = subject_info(INFO)
part_number = (experiment_info['Subject'])
xls = pd.ExcelFile('R://Task_SGT/Documents/Tasks_SGT_testing_log.xlsx')
df = pd.read_excel(xls, 'session2')
delali = df['Delali'][df['ID']=='%s' % part_number].values[0]
gng = df['Go/No Go'][df['ID']=='%s' % part_number].values[0]
sel = df['Self/ Other'][df['ID']=='%s' % part_number].values[0]
sem = df['Semantic'][df['ID']=='%s' % part_number].values[0]

gonogo_index = {'Go':['Go','NoGo','NoGo','Go'],'NoGo':['NoGo','Go','Go','NoGo']}
self_index = {'You':['You','Friend','Friend','You'],'Friend':['Friend','You','You','Friend']}
sem_index = {'Picture':['Picture','Word','Word','Picture'],'Word':['Word','Picture','Picture','Word']}
gonogo_order = gonogo_index[gng]
sem_order = sem_index[sem]
self_order = self_index[sel]
overall_index = {'a':[gonogo_order, sem_order, self_order],'b':[gonogo_order, self_order, sem_order],'c':[sem_order, gonogo_order, self_order],'d':[sem_order, self_order, gonogo_order],'e':[self_order, sem_order, gonogo_order], 'f':[self_order, sem_order, gonogo_order]}

order = overall_index[delali]
order = [item for sublist in order for item in sublist]

ro = df['Run order'][df['ID']=='%s' % part_number].values[0]
ro = int(ro)
run_order = [['1','1','2','2'], ['2','2','1','1'],['1','2','1','2'],['2','1','2','1']][ro]
run_order = run_order*3
count_order = ['1','1','2','2']*3

keypress = df['Keypress'][df['ID']=='%s' % part_number].values[0]

def run_experiment():
    ##########################################
    # collect participant info
    ##########################################
    # set dictionary for instructions in running each trial
    instruction_parameter = dict([
            ('inst_size', 34), # size/height of the instruction
            ('inst_color', 'black'), # color of the instruction
            ('inst_font', 'sans'), # color of the instruction
            ])

    # set dictionary for parameters in running each trial
    trial_parameter = dict([
            ('IS', '+'),  # symbol to display durint ISI)
            ('IS_size', 44), # size/height of the fixation
            ('IS_color', 'black'), # color of the fixation
            ('IS_font', 'sans'), # color of the fixation
            ('StimTxt_size', 64), # size/height of the stimulus text
            ('StimTxt_color', 'black'), # color of the stimulus text
            ('StimTxt_font', 'sans'), # color of the stimulus text
            # the following two are not used ... but the actual size, for the moment
            ('StimImage_size_x', 300), # size x of stimulus image
            ('StimImage_size_y', 300), # size x of stimulus image
            ('Stim_Image_Type', '.bmp'), # include those Subtask that show images
            ('pos_x_gap', 400), # gap to add / subtract to make the presentation towards left or Right from origin (0,0)
            ('pos_y_gap', 220), # gap to add / subtract to make the presentation towardsTop or Bottom from origin (0,0)
            ('num_stim', 2), # number of stimulus within one trial.. max=4 ... check if programme below update this
            ('resp_stay', 0), # should the screen stay until after receiving response input, 0=yes, 1=no
            ('beep_flag', 0), # should there be a beep sound if no response is received, 0=yes, 1=no
            ])


    # set the response set for each trial
    trial_response = dict([
            ('trialstart_time', 0),  # trial start time)
            ('keystart_time', 0),  # trial start time)
            ('resp_key', None), # size/height of the fixation
            ('response', 999), # nth response in the response key list, currently set to [yes, no]
            ('keypress_time', 0), # nth response in the response key list, currently set to [0:yes, 1:no]
            ('key_RT', 0), # Reaction Time 
            ])

    # initialize the output for writing to csv
    trial_output = {}

    # set dictionary for min/max/step duration for ISI presented before the each stimuli (max 4) 
    # IMPORTANT -- these are set for ms ... while clock time is in seconds -- remember to divide by 1000
    # Note:  if any of the ISI_min is set to 0, no IS is displayed.
    ISI_min = dict([
            (0, 500), # before stim1
            (1, 500), # before stim2
            (2, 0), # before stim3
            (3, 0), # before stim4
            ])

    ISI_max = dict([
            (0, 500), # before stim1
            (1, 1500), # before stim2
            (2, 0), # before stim3
            (3, 0), # before stim4
            ])

    ISI_step = dict([
            (0, 0), # before stim1
            (1, 500), # before stim2
            (2, 0), # before stim3
            (3, 0), # before stim4
            ])

    # set dictionary for min/max/step duration for stimuli presentation (max 4) 
    # not working -- If Stim_min is set to 99999, the current stim is displayed with the upcoming stimuli (meaning 2 stimuli displayed together)
    Stim_min = dict([
            (0, 800), # before stim1
            (1, 1500), # before stim2
            (2, 0), # before stim3
            (3, 0), # before stim4
            ])

    Stim_max = dict([
            (0, 800), # before stim1
            (1, 1500), # before stim2
            (2, 0), # before stim3
            (3, 0), # before stim4
            ])

    Stim_step = dict([
            (0, 0), # before stim1
            (1, 0), # before stim2
            (2, 0), # before stim3
            (3, 0), # before stim4
            ])
    ##########################################
    # Setup
    ##########################################
    #
    # set up enviroment variables and generators
    settings = get_settings(
                    env=experiment_info['Environment'],
                    ver=keypress)
    
    ####################
    ### ************ ###
    # programmatically change the number for stimuli for go-nogo task
    ####################
    if subtask in ['Go', 'NoGo']:
        trial_parameter['num_stim'] = 1
        trial_parameter['beep_flag'] = 1
        settings['rec_keys'] = list(settings['rec_keys'][0])
        settings['rec_keyans'] = list(settings['rec_keyans'][0])
        settings['rec_keyans'][0] = 'Go'
        Stim_min[0] = 1500
        Stim_max[0] = 1500
        ISI_min[0] = 500
        ISI_max[0] = 1500
        ISI_step[0] = 500
    ####################
    ### ****end***** ###
    ####################
    
    # set up the trial conditions
    trials, headers=get_trial_generator(subtask, keypress, experiment_info['ESQuestion'], run)
    # setup the trial header, used for logging info
    temp = list(trials[1].items())
    mycount = 0
    for i in range (0, len(headers)):
        if temp[i][1] != 'NA':
            trial_output[headers[i]]=temp[mycount][1]
        mycount += 1
    trial_output_headers = list(trial_output.keys()) + list(trial_response.keys())
    
    # set log file
    logfile = experiment_info['LogFile'].replace(experiment_info['Experiment'], subtask + run + experiment_info['Experiment'])
    event_logger(settings['logging_level'], logfile)

    # create experiment 
    Experiment = Paradigm(escape_key='esc', color=0,
                          window_size=settings['window_size'])
    # hide mouse
    event.Mouse(visible=False)

    ##########################################
    # Set & display instructions
    ##########################################
    # display instruction for first run
    myparse=0
    #if run == '1':
    instr_txt = instr_path + subtask + instr_name
    myparse=1
    # skip instruction in other runs (just press return)
    #else:
        #instr_txt = instr_path + begin_name
    ready_txt = instr_path + ready_name
    instructions_run = my_instructions(
        window=Experiment.window, settings=settings,
        instruction_txt=instr_txt, ready_txt=ready_txt, 
        instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
        instruction_color=instruction_parameter['inst_color'], parseflag=myparse)

#    if run == '1':
    instructions_run.show()
#    else:
#        pass

    
    # setup the fixation cross, assume to be displayed at the same position at the origin 
    fixation = Display_Text(window=Experiment.window, text=trial_parameter['IS'], 
                            size=trial_parameter['IS_size'], color=trial_parameter['IS_color'], 
                            font=trial_parameter['IS_font'], pos_x=0, pos_y=0)
    exp_end_txt = instr_path + exp_end_name
    exp_end_msg = my_instructions(
        window=Experiment.window, settings=settings,
        instruction_txt=exp_end_txt, ready_txt=ready_txt, 
        instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
        instruction_color=instruction_parameter['inst_color'], parseflag=0)

#    exp_end_txt = load_instruction(instr_path + exp_end_name)
#    exp_end_msg = visual.TextStim(Experiment.window, text=exp_end_txt, font=instruction_parameter['inst_font'],
#                              name='instruction', pos=[-50,0], 
#                              height=instruction_parameter['inst_size'], wrapWidth=1100,
#                              color=instruction_parameter['inst_color'])    


    ##########################################
    # Running the experiment
    ##########################################

    # wait trigger if this this in MRI environment (checked inside the function)
    if experiment_info['Environment'] == 'mri':
        instructions_run.waitTrigger(trigger_code)
    # get a global clock
    timer = core.Clock()

    for trialcount in range(0, len(trials)):
 #   for trialcount in range(0, 1):

        for i in range (0, len(trial_output_headers)):
            if trial_output_headers[i] not in list(trial_response.keys()):
                trial_output[trial_output_headers[i]]=trials[trialcount][trial_output_headers[i]]
    
        trial_response['trialstart_time'] = timer.getTime()
#        print(trialcount, trials[trialcount]['Trial_No'], trials[trialcount]['Type'])
        # get current trial from trials read from file
        trial_stim = [trials[trialcount]['Stim1']]
        trial_stim_F1 = [trials[trialcount]['Stim1_F1']]
        trial_stim_F2 = [trials[trialcount]['Stim1_F2']]
        if trial_parameter['num_stim'] > 1:
            trial_stim = trial_stim + [trials[trialcount]['Stim2']]
            trial_stim_F1 = trial_stim_F1 + [trials[trialcount]['Stim2_F1']]
            trial_stim_F2 = trial_stim_F2 + [trials[trialcount]['Stim2_F2']]
        if trial_parameter['num_stim'] > 2:
            trial_stim = trial_stim + [trials[trialcount]['Stim3']]
            trial_stim_F1 = trial_stim_F1 + [trials[trialcount]['Stim3_F1']]
            trial_stim_F2 = trial_stim_F2 + [trials[trialcount]['Stim3_F2']]
        if trial_parameter['num_stim'] > 3:
            trial_stim = trial_stim + [trials[trialcount]['Stim4']]
            trial_stim_F1 = trial_stim_F1 + [trials[trialcount]['Stim4_F1']]
            trial_stim_F2 = trial_stim_F2 + [trials[trialcount]['Stim4_F2']]
            

        
        # display 1-4 stimuli in defined in the current trial
        for stimcount in range(0, trial_parameter['num_stim']):
            #######################################################
            # display fixation - before stim (skip if this is set to 0)
            if ISI_min[stimcount] != 0: # not to display IS if ISI_min is set to 0
                mytime = fixation.show(timer)
                if ISI_min[stimcount] == ISI_max[stimcount]:
                    myduration=ISI_min[stimcount]
                else:
                    myduration=random.randrange(ISI_min[stimcount], ISI_max[stimcount]+1, ISI_step[stimcount])
                core.wait(myduration/1000)

            #######################################################
            # set the current stimulus positions, x, y defined by F1[0], and text feature defined by F1[1]
            mytext=trial_stim[stimcount]
            mypos_x = 0;
            mypos_y = 0;
            for i in range (0, len(trial_stim_F1[stimcount])):
                if i == 0:  # set position
                    if trial_stim_F1[stimcount][i] == 'L':
                        mypos_x = mypos_x - trial_parameter['pos_x_gap']
                    elif trial_stim_F1[stimcount][i] == 'R':
                        mypos_x = mypos_x + trial_parameter['pos_x_gap']
                    if trial_stim_F1[stimcount][i] == 'B':
                        mypos_y = mypos_y - trial_parameter['pos_y_gap']
                    elif trial_stim_F1[stimcount][i] == 'T':
                        mypos_y = mypos_y + trial_parameter['pos_y_gap']
                elif i == 1 or i == 2:    # set text characteristics
                    if trial_stim_F1[stimcount][i] == 'U':
                        mytext = trial_stim[stimcount].upper()
                    elif trial_stim_F1[stimcount][i] == 'L':
                        mytext = trial_stim[stimcount].lower()
                    elif trial_stim_F1[stimcount][i] == 'S':
                        mytext = list(trial_stim[stimcount])
                        random.shuffle(mytext)
                        mytext = ''.join(mytext)
                    

            #######################################################
            # setup the current stimulus for display, text or image

            if trial_parameter['Stim_Image_Type'] in trial_stim[stimcount]:  # for image display
#                trial_parameter['StimImage_size_x'], size_y=trial_parameter['StimImage_size_y'] = cv.GetSize(trial_stim[stimcount])
                cur_stim = Display_Image_act(window=Experiment.window, image=trial_stim[stimcount], 
#                                          size_x=trial_parameter['StimImage_size_x'], size_y=trial_parameter['StimImage_size_y'], 
                                          pos_x=mypos_x, pos_y=mypos_y)
            else:
                cur_stim = Display_Text(window=Experiment.window, text=mytext, 
                                        size=trial_parameter['StimTxt_size'], color=trial_parameter['StimTxt_color'], 
                                        font=trial_parameter['StimTxt_font'], pos_x=mypos_x, pos_y=mypos_y)

            #######################################################
            # display the current stimulus-text 
            if Stim_min[stimcount] == 9999:    # not to display yet (if 999), wait read the next stimuli first (need more codings)
                print('Do nothing now')
            else:
                mytime = cur_stim.show(timer)

                # calculate the duration time
                if Stim_min[stimcount] == Stim_max[stimcount] or Stim_step[stimcount] == 0:
                    myduration=Stim_min[stimcount]
                else:
                    myduration=random.randrange(Stim_min[stimcount], Stim_max[stimcount]+1, Stim_step[stimcount])
                
                # if this is the last trial, wait for key press OR when duration for this stim lapses
                if stimcount == trial_parameter['num_stim'] -1:
                    trial_response['keystart_time'], trial_response['resp_key'], trial_response['response'], trial_response['keypress_time'], trial_response['key_RT'] = Get_Response(timer, myduration/1000, settings['rec_keys'], settings['rec_keyans'], trial_parameter['beep_flag'])
                    if trial_parameter['resp_stay'] == 0:  # stay until duration
                        Experiment.window.flip()  # clear the window
                        core.wait(myduration/1000 - trial_response['key_RT']) # wait for duration
                    
                    for i in range(0, len(list(trial_response.keys()))):
                        trial_output[list(trial_response.keys())[i]]=list(trial_response.items())[i][1]
                    datafile = experiment_info['DataFile'].replace(experiment_info['Experiment'], subtask + '_' + keypress + run + '_' + count + '_' + experiment_info['Experiment'])
                    # write response to data file
                    full_path = os.path.abspath(datafile)
                    write_csv(datafile, trial_output_headers, trial_output)
                    

                # else, it is NOT the last stimuli in trial, wait for presentation of the stimuli
                else:
                    core.wait(myduration/1000) # wait for duration
    
        
        
    ##########################################
    # Finishing the experiment
    ##########################################
    # ending message
    exp_end_msg.show()
#    exp_end_msg.draw()
#    Experiment.window.flip()
#    event.waitKeys(keyList=['return'])

    logging.flush()
    # change output files to read only
    read_only(datafile)
    read_only(logfile)
    # quit

    ##########################################
    # Running the Experience Sampling Questionnarire
    ##########################################
    if experiment_info['ESQuestion'] == 'ES':

        ESQ_txt = instr_path + ESQ_name
        ESQ_msg = my_instructions(
                window=Experiment.window, settings=settings,
                instruction_txt=ESQ_txt, ready_txt=ready_txt, 
                instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
                instruction_color=instruction_parameter['inst_color'], parseflag=0)
        ESQ_msg.show()
        
        ES_fixed = data.TrialHandler(nReps = 1, method = 'sequential', trialList = data.importConditions(fixed_ESQ_name), name = 'Questionnaire') 
        ES_random = data.TrialHandler(nReps = 1, method = 'random', trialList = data.importConditions(random_ESQ_name), name = 'Questionnaire')
        
        # Note: this is the order of the output header, very specific, just to conform with others
        ESQ_key = ['Participant_number', 'Questionnaire_startTime', 'Questionnaire_endTime', 'TrialDuration', 'Task', 'Version', 'Keypress', 'Run', 'Focus', 'Future', 'Past', 'Self', 'Other', 'Emotion', 'Modality', 'Detailed', 'Deliberate', 'Problem', 'Diversity', 'Intrusive', 'Source', 'Arousal', 'Tense', 'Uncertainty']            
    
        ratingScale = visual.RatingScale(Experiment.window, low=1, high=10, markerStart=4.5,
                precision=10, tickMarks=[1, 10],
                leftKeys='1', rightKeys='2', acceptKeys='4')
        QuestionText = visual.TextStim(Experiment.window, color = 'white', text = None , alignHoriz = 'center', alignVert= 'top', height=34)
        scale_high = visual.TextStim(Experiment.window, text=None, height=34, wrapWidth=1100, pos=[300,-150],color='white', font=sans)
        scale_low = visual.TextStim(Experiment.window, text=None, height=34, wrapWidth=1100, pos=[-300,-150],color='white', font=sans)
        thisRunDict = {'Participant_number': experiment_info['Subject']}
        thisRunDict['Questionnaire_startTime'] = cur_stim.show(timer)
        thisRunDict['Task'] = subtask
        thisRunDict['Run'] = count
        thisRunDict['Version'] = run
        thisRunDict['Keypress'] = keypress
    
#       get each question from Questionnaire:
        for i in range(0, len(ES_fixed.trialList + ES_random.trialList)):
            if i < len(ES_fixed.trialList):
                question = ES_fixed.next()
            else:
                question = ES_random.next()
            ratingScale.noResponse = True
            keyState=key.KeyStateHandler()
            Experiment.window.winHandle.push_handlers(keyState)

            pos = ratingScale.markerStart
            inc=0.1
            while ratingScale.noResponse:  #key 4 not pressed
                if keyState[key._1] is True:
                    pos -= inc
                elif keyState[key._2] is True:
                    pos += inc
                if pos > 9:
                    pos = 9
                elif pos < 0:
                    pos = 0
            
                ratingScale.setMarkerPos(pos)
                QuestionText.setText(question['Questions'])
                QuestionText.draw()
                scale_high.setText(question['Scale_high'])
                scale_low.setText(question['Scale_low'])
                scale_high.draw()
                scale_low.draw()
                ratingScale.draw()
                Experiment.window.flip()

            responded = ratingScale.getRating()
            thisRunDict[ str(question['Label'] )] = str(responded) 

        thisRunDict['Questionnaire_endTime'] = cur_stim.show(timer)
        thisRunDict['TrialDuration'] = thisRunDict['Questionnaire_endTime'] - thisRunDict['Questionnaire_startTime']
        filename = experiment_info['DataFile'].replace('.csv', 'endQs.csv')
#        write_csv(filename, thisRunDict.keys(), thisRunDict)
        write_csv(filename, ESQ_key, thisRunDict)



##########################################
# This is the main programme
##########################################
# now run this thing
if __name__ == "__main__":
    # set working directory as the location of this file
    _thisDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_thisDir)

    for subtask, run, count in zip(order, run_order, count_order):
        run_experiment()

core.quit()
