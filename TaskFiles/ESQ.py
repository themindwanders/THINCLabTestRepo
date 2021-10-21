from src.library import *
import os
import sys
import random
from psychopy import core, event, logging, visual, data
import time


def runexp(filename, timer, win, writer, resdict, trialnum):
    
    win.flip() 
    
    instruction_parameter = dict([
                ('inst_size', 34), # size/height of the instruction
                ('inst_color', 'black'), # color of the instruction
                ('inst_font', 'sans'), # color of the instruction
                ])

    INFO = {
            'Experiment': 'Task2019',  # compulsory: name of program, used for trial definition in ./parameter/~.csv
            'Subject': '001',  # compulsory
            'Version': ['A', 'B'],  # counterbalance the fixation color
            'Run': '1',  # compulsory
            #'Subtask': ['Self', 'Other'],  # start the task with block for Self or Other
            'Subtask': ['Word', 'Picture', 'You', 'Friend', 'Go', 'NoGo'],  # start the task with block for Image or Word
            'Environment': ['lab', 'mri'],  # mri version can be tested on a normal stimuli delivery pc
            'ESQuestion': ['ES', 'No ES'], # with or without experience sampling
            }
    ready_txt = instr_path + ready_name

    #experiment_info = subject_info(INFO)
    settings = get_settings(
                        env='lab',
                        ver='A')
    #Experiment = Paradigm(escape_key='esc', color=0
    #                          )#window_size=settings['window_size'])
        # hide mouse


    ESQ_txt = instr_path + ESQ_name
    ESQ_msg = my_instructions(
            window=win, settings=settings,
            instruction_txt=ESQ_txt, ready_txt=ready_txt, 
            instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
            instruction_color='black', parseflag=0)
    ESQ_msg.display.setText("""
Please answer the questions honestly.

A list of descriptions and a rating scale ranging from 1 to 10 will be presented on the screen.

Please use the left and right arrow keys to select your answer, and the enter button to confirm.
"""
    )
    ESQ_msg.display.draw()
    ESQ_msg.window.flip()
        
    event.waitKeys(keyList=['return'])
    #ESQ_msg.show()
    win.flip()

    ES_fixed = data.TrialHandler(nReps = 1, method = 'sequential', trialList = data.importConditions(fixed_ESQ_name), name = 'Questionnaire') 
    ES_random = data.TrialHandler(nReps = 1, method = 'random', trialList = data.importConditions(random_ESQ_name), name = 'Questionnaire')

    # Note: this is the order of the output header, very specific, just to conform with others
    ESQ_key = ['Participant_number', 'Questionnaire_startTime', 'Questionnaire_endTime', 'TrialDuration', 'Focus', 'Future', 'Past', 'Self', 'Other', 'Emotion', 'Modality', 'Detailed', 'Deliberate', 'Problem', 'Diversity', 'Intrusive', 'Source', 'Arousal', 'Tense', 'Uncertainty']            

    ratingScale = visual.RatingScale(win, low=1, high=10, markerStart=4.5,
            precision=10, tickMarks=[1, 10], markerColor='black', textColor='black', lineColor='black',acceptPreText='Use the left and right arrow keys',acceptSize=3
            )
    QuestionText = visual.TextStim(win, color = 'black', text = None , anchorHoriz = 'center', anchorVert= 'top')
    scale_high = visual.TextStim(win, text=None,  wrapWidth=None,color='black', pos=(0.5,-0.5))
    scale_low = visual.TextStim(win, text=None, wrapWidth=None, color='black',pos=(-0.5,-0.5))
    
    

    #       get each question from Questionnaire:
    for enum, i in enumerate(range(0, len(ES_fixed.trialList))):
        if enum < trialnum:
            if i < len(ES_fixed.trialList):
                question = ES_fixed.next()
            ratingScale.noResponse = True
            ratingScale
            keyState=key.KeyStateHandler()
            win.winHandle.push_handlers(keyState)

            pos = ratingScale.markerStart
            inc=0.1
            while ratingScale.noResponse:  #key 4 not pressed
                if keyState[key.LEFT] is True:
                    pos -= inc
                elif keyState[key.RIGHT] is True:
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
                win.flip()
            time.sleep(1)
            responded = ratingScale.getRating()

            resdict['Timepoint'], resdict['Time'], resdict['Experience Sampling Question'], resdict['Experience Sampling Response'] = 'ESQ', timer.getTime(), str(question['Label']), responded
            
            writer.writerow(resdict)
            
            resdict['Timepoint'], resdict['Time'],resdict['Experience Sampling Question'],resdict['Experience Sampling Response'] = None,None,None,None
        

    
    
    




    end_txt = instr_path + end_name
    end_msg = my_instructions(
            window=win, settings=settings,
            instruction_txt=end_txt, ready_txt=ready_txt, 
            instruction_size=instruction_parameter['inst_size'], instruction_font=instruction_parameter['inst_font'],
            instruction_color=instruction_parameter['inst_color'], parseflag=0)
    #end_msg.show()


