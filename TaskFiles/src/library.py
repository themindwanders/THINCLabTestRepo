# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 15:25:41 2019

@author: nh1037
"""

from psychopy import core, data, gui, visual, event, logging
import winsound
from pyglet.window import key
from random import uniform, shuffle
import numpy as np
import os
import codecs
import csv
import re
import stat
from collections import OrderedDict


#from src.fileIO import *
#from src.datastructure.datastructure import *
#from src.datastructure.stimulus import tup2str


###################################################
# file locations
#instr_txt = './instructions/exp_instr.txt'  # instruction: start of experiment
instr_path = './instructions/'  # path for instructions
instr_name = '_instr.txt' # filename (preceded by subtask name) for instructions
begin_name = 'begin_instr.txt' # beginning text, if no instruction is needed for second run
ready_name = 'wait_trigger.txt' # instruction: wait trigger screen
exp_end_name = 'taskend_instr.txt' # instruction: wait trigger screen
ESQ_name = 'ESQ_instr.txt'
end_name = 'end_instr.txt'
trial_setup_path = './parameters/' # path for trial setup
fixed_ESQ_name = './parameters/fixedQuestions.csv' # experience sampling questions - fixed
random_ESQ_name = './parameters/questions.csv' # experience sampling questions - random


###################################################
# Base settings that apply to all environments.
# These settings can be overwritten by any of the
# environment settings.
BASE = {
    'test': False,
    'mouse_visible': False,
#    'logging_level': logging.INFO
    'logging_level': logging.ERROR,
}

# Laboratory setting
LAB = {
    'env': 'lab',  # Enviroment name
    #'window_size': 'full_screen',
    #'window_size': (1280, 720),
    'window_size': 'full_screen',
    'input_method': 'keyboard'
    }

MRI = {
    'env': 'mri',
    'window_size': 'full_screen',
    'input_method': 'serial',
}

# experiment specific vesion related setting
VER_A = {
        'txt_color': 'black',
        'rec_keys': ['left', 'right'],
        'rec_keyans': ['Yes', 'No'],
        }

VER_B = {
        'txt_color': 'black',
        'rec_keys': ['left', 'right'],
        'rec_keyans': ['Yes', 'No'],
        }

VER_A_MRI = {
            'rec_keys': ['1', '2'],
            'loc_keys': ['6', '7']
            }

VER_B_MRI = {
            'rec_keys': ['6', '7'],
            'loc_keys': ['1', '2']
            }

sans = ['Arial','Gill Sans MT', 'Helvetica','Verdana'] #use the first font found on this list


def get_trial_generator(subtask, version, run_no, numoftrials):
#def get_trial_generator(subtask, version):
    '''
    get the list of parameters (stimuli) from the .csv 
    '''
    
    trial_path = trial_setup_path + subtask + '_' + version + str(run_no) + '.csv'   
    trialpool, trialhead = load_trials(trial_path, numoftrials)
    
#    if ESQuestion == 'ES':
#        question2, _ = load_conditions_dict(random_ESQ_name)       
        #exp_sample_generator = stimulus_ExpSample(question2)
#        question1, _ = load_conditions_dict(fixed_ESQ_name)
#        questions = question1 + question2
    
    return trialpool, trialhead


def get_settings(env, ver):
    '''Return a dictionary of settings based on
    the specified environment, given by the parameter
    env. Can also specify whether or not to use testing settings.

    Include keypress counter balancing
    '''
    # Start with the base settings
    settings = BASE


    if env == 'lab':
        settings.update(LAB)

        # display and key press counter balancing
        if ver == 'A':
            settings.update(VER_A)
        elif ver == 'B':
            settings.update(VER_B)
        else:
            raise ValueError('Version "{0}" not supported.'.format(ver))

    elif env == 'mri':
        settings.update(MRI)
        # display and key press counter balancing
        if ver == 'A':
            settings.update(VER_A_MRI)
        elif ver == 'B':
            settings.update(VER_B_MRI)
        else:
            raise ValueError('Version "{0}" not supported.'.format(ver))

    else:
        raise ValueError('Environment "{0}" not supported.'.format(env))


    return settings




##################################################
# experiment
class Paradigm(object):
    '''
    Study paradigm
    '''
    def __init__(self, escape_key='esc', window_size=(1280, 720), color='black', *args, **kwargs):
        self.escape_key = escape_key
        self.trials = []
        self.stims = {}

        if window_size =='full_screen':
            #self.window = visual.Window(fullscr=True, color=color, units='pix', *args, **kwargs)
            self.window = visual.Window(size=window_size, color=color, allowGUI=True, units='pix', *args, **kwargs)
        else:
            self.window = visual.Window(size=window_size, color=color, allowGUI=True, units='pix', *args, **kwargs)


class Display_Text(object):
    '''
    show text in the screen at x,y
    '''
    def __init__(self, window, text, size, color, font, pos_x, pos_y):
        '''Initialize a text stimulus.
        Args:
        window - The window object
        text - text to display
        size, color, font - attributes of the text
        pos_x, pos_y - x,y position, 0,0 is the centre
        '''
        self.window = window
        self.text = text
        self.display = visual.TextStim(
                window, text=text, font=font,
                #name='instruction',
                pos=[pos_x, pos_y],  wrapWidth=1100,
                color='black'
                ) #object to display instructions

    def show(self, clock):
        self.display.draw()
        self.window.flip()
        start_trial = clock.getTime()

        return start_trial


class Display_Image(object):
    '''
    show image in the screen at x,y
    '''
    def __init__(self, window, image, size_x, size_y, pos_x, pos_y):
        '''Initialize a text stimulus.
        Args:
        window - The window object
        image - image to display
        size - attributes of the image
        pos_x, pos_y - x,y position, 0,0 is the centre
        '''
        self.window = window
        #self.window = image
        self.display = visual.ImageStim(self.window, image=image,
                size=[size_x, size_y], pos=[pos_x, pos_y]
                ) #object to display instructions

    def show(self, clock):
        self.display.draw()
        self.window.flip()
        start_trial = clock.getTime()

        return start_trial

# same as Display_Image but using the actual size
class Display_Image_act(object):
    '''
    show image in the screen at x,y
    '''
    def __init__(self, window, image, pos_x, pos_y):
        '''Initialize a text stimulus.
        Args:
        window - The window object
        image - image to display
        size - attributes of the image
        pos_x, pos_y - x,y position, 0,0 is the centre
        '''
        self.window = window
        #self.window = image
        self.display = visual.ImageStim(self.window, image=image,
#                size=[size_x, size_y], 
                pos=[pos_x, pos_y]
                ) #object to display instructions

    def show(self, clock):
        self.display.draw()
        self.window.flip()
        start_trial = clock.getTime()

        return start_trial



def Get_Response(clock, duration, respkeylist, keyans, beepflag):
    
    respRT = np.nan
    KeyResp = None
    Resp = None
    KeyPressTime = np.nan

    event.clearEvents() # clear the keyboard buffer
    #myclock = core.Clock() # start a clock for this response trial
    resp_start  = clock.getTime()

    while KeyResp is None and (clock.getTime() <= resp_start + duration):
        
        # get key press and then disappear
        KeyResp, Resp, KeyPressTime = get_keyboard(
            clock, respkeylist, keyans)

    # get reaction time and key press
    if not np.isnan(KeyPressTime):
        respRT = KeyPressTime - resp_start
    else:
        KeyResp, Resp = 'None', 'None'
        if beepflag == 0:
            winsound.Beep(1000, 100)  # make a beep if no response is made
    
    return resp_start, KeyResp, Resp, KeyPressTime, respRT


def get_keyboard(timer, respkeylist, keyans):
    '''
    Get key board response
    '''
    Resp = None
    KeyResp = None
    KeyPressTime = np.nan
    keylist = ['escape'] + respkeylist

    for key, time in event.getKeys(keyList=keylist, timeStamped=timer):
        if key in ['escape']:
            quitEXP(True)
        else:
            KeyResp, KeyPressTime = key, time
    # get what the key press means
    if KeyResp:
        Resp = keyans[respkeylist.index(KeyResp)]
    return KeyResp, Resp, KeyPressTime


def quitEXP(endExpNow):
    if endExpNow:
        print ('user cancel')
        core.quit()


class my_instructions(object):
    '''
    show instruction and wait for trigger
    '''
    def __init__(self, window, settings, instruction_txt, ready_txt, instruction_size, instruction_font, instruction_color, parseflag):
        self.window = window
        self.settings = settings
        self.env = settings['env']
        self.instruction_txt = load_instruction(instruction_txt)
        self.ready_txt = load_instruction(ready_txt)[0]
        self.display = visual.TextStim(
                window, text='default text', font=instruction_font,
                name='instruction', color='black')#,
                #pos=[-50,0], height=instruction_size, wrapWidth=1100)
                #color=instruction_color
                #) #object to display instructions
        self.parseflag = parseflag

    def parse_inst(self):

        

        return self.instruction_txt

    def showf(self):
        with open('C:/Users/Ian/Documents/TaskRepo/instructions/You_instr.txt') as f:
            lines = f.readlines()
        instext = lines

        
        # substitue keys in the instruction text before displaying the instruction        
        if self.parseflag == 1:
            self.parse_inst()
        self.display.setText(instext)
        self.display.draw()
        self.window.flip()
        
        event.waitKeys(keyList=['return'])

    def waitTrigger(self, trigger_code):
        # wait for trigger in mri environment
        self.display.setText(self.ready_txt)
        self.display.draw()
        self.window.flip()

        if self.env == 'lab':
            core.wait(0)
        elif self.env == 'mri':
            event.waitKeys(keyList=[trigger_code])
        else: # not supported
            raise Exception('Unknown environment setting')

def load_instruction(PATH):
    '''
    load and then parse instrucition
    return a list
    '''

    with codecs.open(PATH, 'r', encoding='utf8') as f:
        input_data = f.read()

    text = parse_instructions(input_data)

    return text


def parse_instructions(input_data):
    '''
    parse instruction into pages
    page break is #
    '''

    text = re.findall(r'([^#]+)', input_data) # match any chars except for #

    return text



def subject_info():
    '''
    get subject information
    return a dictionary
    '''
    #dlg_title = '{} subject details:'.format(experiment_info['Experiment'])
    #infoDlg = gui.DlgFromDict(experiment_info, title=dlg_title)
    experiment_info = {}
    experiment_info['Date'] = data.getDateStr()
    experiment_info['Version'] = "A"
    experiment_info['Subtask'] = "Friend"
    experiment_info['ESQuestion'] = "ES"
    experiment_info['Environment'] = "lab"
    #experiment_info['Date']
    #experiment_info['Date']
    #experiment_info['Date']

   
    file_root = ('_').join([experiment_info['Subject'], experiment_info['Experiment'], 
                            experiment_info['Date']])


    experiment_info['DataFile'] = 'data' + os.path.sep + file_root + '.csv'
    experiment_info['LogFile'] = 'data' + os.path.sep + file_root + '.log'

    if experiment_info['Environment'] == 'mri':
        experiment_info['MRIFile'] = 'data' + os.path.sep + file_root + '_voltime.csv'

    return experiment_info
    #if infoDlg.OK:
    #    return experiment_info
    #else:
        #core.quit()
        #print ('User cancelled')

def create_dir(directory):
    '''

    create a directory if it doesn't exist.

    '''
    if not os.path.exists(directory):
        os.makedirs(directory)



def event_logger(logging_level, LogFile):
    '''
    log events
    '''
    directory = os.path.dirname(LogFile)
    create_dir(directory)

    logging.console.setLevel(logging.WARNING)
    logging.LogFile(LogFile, level=logging_level)


def Write_Response(fileName, list_headers, thisTrial):
    '''
    append the data of the current trial to the data file
    if the data file has not been created, this function will create one


    attributes

    fileName: str
        the file name generated when capturing participant info

    list_headers: list
        the headers in a list, will pass on to function create_headers

    thisTrial: list
        list storing
    '''

    full_path = os.path.abspath(fileName)
    directory = os.path.dirname(full_path)
    create_dir(directory)
    fieldnames = create_headers(list_headers)

    if not os.path.isfile(full_path):
        # headers and the first entry
        with codecs.open(full_path, 'ab+', encoding='utf8') as f:
            dw = csv.DictWriter(f, fieldnames=fieldnames)
            dw.writeheader()
            dw.writerow(thisTrial)
    else:
        with codecs.open(full_path, 'ab+', encoding='utf8') as f:
            dw = csv.DictWriter(f, fieldnames=fieldnames)
            dw.writerow(thisTrial)

class stimulus_ExpSample(object):
    '''
    experience sampling stimulus generator
    save features and generate stimuli

    features: list, dictionaries of questions

    '''
    def __init__(self, features):
        '''split questions into two sets'''
        self.q_focus = [features[0]]  # the focus question stays at the top
        self.q_others = features[1:]

    def generate(self):
        '''yield self.stimuli'''
        shuffle(self.q_others)
        yield self.q_focus + self.q_others


def load_trials(infile, numoftrials):
    '''
    load each row as a dictionary with the headers as the keys
    save the headers in its original order for data saving
    '''

    with codecs.open(infile, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        trials = []

        for enum, row in enumerate(reader):
            if enum < numoftrials:
                trials.append(row)

        # save field names as a list in order
        fieldnames = reader.fieldnames

    return trials, fieldnames


def load_conditions_dict(conditionfile):
    '''
    load each row as a dictionary with the headers as the keys
    save the headers in its original order for data saving
    '''

    with codecs.open(conditionfile, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        trials = []

        for row in reader:
            trials.append(row)

        # save field names as a list in order
        fieldnames = reader.fieldnames

    return trials, fieldnames


def create_headers(list_headers):
    '''
    create ordered headers for the output data csv file
    '''

    headers = []

    for header in list_headers:
        headers.append((header, None))

    return OrderedDict(headers)
        
        
def write_csv(fileName, list_headers, thisTrial):
    '''
    append the data of the current trial to the data file
    if the data file has not been created, this function will create one


    attributes

    fileName: str
        the file name generated when capturing participant info

    list_headers: list
        the headers in a list, will pass on to function create_headers

    thisTrial: dict
        a dictionary storing the current trial
    '''

    full_path = os.path.abspath(fileName)
    directory = os.path.dirname(full_path)
    create_dir(directory)
    fieldnames = create_headers(list_headers)

    if not os.path.isfile(full_path):
        # headers and the first entry
        with codecs.open(full_path, 'ab+', encoding='utf8') as f:
            dw = csv.DictWriter(f, fieldnames=fieldnames)
            dw.writeheader()
            dw.writerow(thisTrial)
    else:
        with codecs.open(full_path, 'ab+', encoding='utf8') as f:
            dw = csv.DictWriter(f, fieldnames=fieldnames)
            dw.writerow(thisTrial)

def read_only(path):
    '''
    change the mode to read only
    '''
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)