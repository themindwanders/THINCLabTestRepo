# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:47:22 2019

"""
import os
import sys
import random
from psychopy import core, event, logging, visual, data
import time

from src.library import *




def run_experiment(timer, win, writer, resdict,trialnums):
    
    ##########################################
    # collect participant info
    ##########################################
    #experiment_info = subject_info()

    ##########################################
    # Setup
    ##########################################
    #
    # set up enviroment variables and generators
    settings = get_settings(
                    env='lab',
                    ver='A')
    
    ####################
    ### ************ ###
    # programmatically change the number for stimuli for go-nogo task
    ####################
    #if experiment_info['Subtask'] in ['Go', 'NoGo']:
    trial_parameter['num_stim'] = 1
    trial_parameter['beep_flag'] = 1
    del settings['rec_keys'][1]
    del settings['rec_keyans'][1]
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
    trials, headers=get_trial_generator("Friend", 'A', 1, trialnums)
    # setup the trial header, used for logging info
    temp = list(trials[1].items())
    mycount = 0
    for i in range (0, len(headers)):
        if temp[i][1] != 'NA':
            trial_output[headers[i]]=temp[mycount][1]
        mycount += 1
    trial_output_headers = list(trial_output.keys()) + list(trial_response.keys())
    
    
    # set log file
    #logloc = 'rando.csv'
    #event_logger(settings['logging_level'], logloc)

    # create experiment 
    #Experiment = Paradigm(escape_key='esc', color=0
    #                      )#window_size=settings['window_size'])
    #win = visual.Window(allowGUI=True, units='pix')
    # hide mouse
    event.Mouse(visible=False)

    ##########################################
    # Set & display instructions
    ##########################################
    # display instruction for first run
    myparse=0
    #if experiment_info['Run'] == '1':
    instr_txt = instr_path + 'You' + instr_name
    myparse=1
    # skip instruction in other runs (just press return)
    #else:
        #instr_txt = instr_path + begin_name
    ready_txt = instr_path + ready_name
    instructions_run = my_instructions(
        window=win, settings=settings,
        instruction_txt=instr_txt, ready_txt=ready_txt, 
        instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
        instruction_color='black', parseflag=myparse)

#    if experiment_info['Run'] == '1':
    instructions_run.showf()
#    else:
#        pass

    
    # setup the fixation cross, assume to be displayed at the same position at the origin 
    fixation = Display_Text(window=win, text=trial_parameter['IS'], 
                            size=trial_parameter['IS_size'], color=trial_parameter['IS_color'], 
                            font=trial_parameter['IS_font'], pos_x=0, pos_y=0)
    exp_end_txt = instr_path + exp_end_name
    exp_end_msg = my_instructions(
        window=win, settings=settings,
        instruction_txt=exp_end_txt, ready_txt=ready_txt, 
        instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
        instruction_color=instruction_parameter['inst_color'], parseflag=0)

#    exp_end_txt = load_instruction(instr_path + exp_end_name)
#    exp_end_msg = visual.TextStim(win, text=exp_end_txt, font=instruction_parameter['inst_font'],
#                              name='instruction', pos=[-50,0], 
#                              height=instruction_parameter['inst_size'], wrapWidth=1100,
#                              color=instruction_parameter['inst_color'])    


#     ##########################################
#     # Running the experiment
#     ##########################################

    # wait trigger if this this in MRI environment (checked inside the function)
    
    trial_parameter['num_stim'] = 2

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
                cur_stim = Display_Image_act(window=win, image=trial_stim[stimcount], 
#                                          size_x=trial_parameter['StimImage_size_x'], size_y=trial_parameter['StimImage_size_y'], 
                                          pos_x=mypos_x, pos_y=mypos_y)
            else:
                cur_stim = Display_Text(window=win, text=mytext, 
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
                        win.flip()  # clear the window
                        core.wait(myduration/1000 - trial_response['key_RT']) # wait for duration
                    
                    for i in range(0, len(list(trial_response.keys()))):
                        trial_output[list(trial_response.keys())[i]]=list(trial_response.items())[i][1]

                    # write response to data file
                    #write_csv(logloc, trial_output_headers, trial_output)
                    resdict['Timepoint'] = trial_stim
                    resdict['Time'] = mytime
                    writer.writerow(resdict) 
                    resdict['Timepoint'], resdict['Time'] = None, None

                # else, it is NOT the last stimuli in trial, wait for presentation of the stimuli
                else:
                    core.wait(myduration/1000) # wait for dura
                    
    
    #write_csv(logloc, trial_output_headers, trial_output)    
    
    ##########################################
    # Finishing the experiment
    ##########################################
        
    # ending message
    #exp_end_msg.show()
#    exp_end_msg.draw()
#    win.flip()
#    event.waitKeys(keyList=['return'])

    logging.flush()
    # change output files to read only
    
    # quit

    ##########################################
    # Running the Experience Sampling Questionnarire
    ##########################################
#     if experiment_info['ESQuestion'] == 'ES':

#         ESQ_txt = instr_path + ESQ_name
#         ESQ_msg = my_instructions(
#                 window=win, settings=settings,
#                 instruction_txt=ESQ_txt, ready_txt=ready_txt, 
#                 instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
#                 instruction_color=instruction_parameter['inst_color'], parseflag=0)
#         ESQ_msg.show()
        
#         ES_fixed = data.TrialHandler(nReps = 1, method = 'sequential', trialList = data.importConditions(fixed_ESQ_name), name = 'Questionnaire') 
#         ES_random = data.TrialHandler(nReps = 1, method = 'random', trialList = data.importConditions(random_ESQ_name), name = 'Questionnaire')
        
#         # Note: this is the order of the output header, very specific, just to conform with others
#         ESQ_key = ['Participant_number', 'Questionnaire_startTime', 'Questionnaire_endTime', 'TrialDuration', 'Focus', 'Future', 'Past', 'Self', 'Other', 'Emotion', 'Modality', 'Detailed', 'Deliberate', 'Problem', 'Diversity', 'Intrusive', 'Source', 'Arousal', 'Tense', 'Uncertainty']            
    
#         ratingScale = visual.RatingScale(win, low=1, high=10, markerStart=4.5,
#                 precision=10, tickMarks=[1, 10],
#                 leftKeys='1', rightKeys='2', acceptKeys='4')
#         QuestionText = visual.TextStim(win, color = 'white', text = None , alignHoriz = 'center', alignVert= 'top', height=34)
#         scale_high = visual.TextStim(win, text=None, height=34, wrapWidth=1100, pos=[300,-150],color='white', font=sans)
#         scale_low = visual.TextStim(win, text=None, height=34, wrapWidth=1100, pos=[-300,-150],color='white', font=sans)
#         thisRunDict = {'Participant_number': experiment_info['Subject']}
#         thisRunDict['Questionnaire_startTime'] = 0
    
# #       get each question from Questionnaire:
#         for i in range(0, len(ES_fixed.trialList + ES_random.trialList)):
#             time.sleep(1)
#             if i < len(ES_fixed.trialList):
#                 question = ES_fixed.next()
#             else:
#                 question = ES_random.next()
#             ratingScale.noResponse = True
#             keyState=key.KeyStateHandler()
#             win.winHandle.push_handlers(keyState)

#             pos = ratingScale.markerStart
#             inc=0.1
#             while ratingScale.noResponse:  #key 4 not pressed
#                 if keyState[key._1] is True:
#                     pos -= inc
#                 elif keyState[key._2] is True:
#                     pos += inc
#                 if pos > 9:
#                     pos = 9
#                 elif pos < 0:
#                     pos = 0
            
#                 ratingScale.setMarkerPos(pos)
#                 QuestionText.setText(question['Questions'])
#                 QuestionText.draw()
#                 scale_high.setText(question['Scale_high'])
#                 scale_low.setText(question['Scale_low'])
#                 scale_high.draw()
#                 scale_low.draw()
#                 ratingScale.draw()
#                 win.flip()

#             responded = ratingScale.getRating()
#             thisRunDict[ str(question['Label'] )] = str(responded) 

#         thisRunDict['Questionnaire_endTime'] = 0
#         thisRunDict['TrialDuration'] = thisRunDict['Questionnaire_endTime'] - thisRunDict['Questionnaire_startTime']
#         filename = experiment_info['DataFile'].replace('.csv', 'endQs.csv')
# #        write_csv(filename, thisRunDict.keys(), thisRunDict)
#         write_csv(filename, ESQ_key, thisRunDict)




        # end_txt = instr_path + end_name
        # end_msg = my_instructions(
        #         window=win, settings=settings,
        #         instruction_txt=end_txt, ready_txt=ready_txt, 
        #         instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
        #         instruction_color=instruction_parameter['inst_color'], parseflag=0)
        # end_msg.show()

    ##########################################
    # Finishing
    ##########################################

    

    #win.close()
    #core.quit()


def runexp(filename, timer, win, writer, resdict,trialnums):
    global instruction_parameter
    global trial_output
    global ISI_min
    global ISI_max
    global Stim_max
    global Stim_min
    global trial_parameter
    
    global ISI_step
    global trial_response
    global trigger_code
    global Stim_step
    

   
    # get input for dictionary defining the environment & trials to run
    

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
            ('beep_flag', 1), # should there be a beep sound if no response is received, 0=yes, 1=no
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

    # MRI related settings
    dummy_vol = 0
    tr = 2
    trigger_code = '5'
    
    run_experiment(timer, win, writer, resdict,trialnums)


##########################################
# This is the main programme
##########################################
# now run this thing


