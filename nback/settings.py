# -*- coding: utf-8 -*-

'''settings.py
Define global and environment-specific settings here.
'''
# there's a bug in datastructure so don't change the next two lines
BLOCK_TIME = 12
BLOCK_GO_N = 16

# set the two features we used for making the stimulus
shape = ['square', 'triangle', 'circle']
# texture = ['dot', 'solid', 'stripe']

# locate path of experiment specification related files
condition_path = None  # set later by subject info input
trialheader_path = './parameters/TrialHeaders.csv'
trialspec_path = './parameters/TrialSpecifications.csv'
stimulus_dir = './stimuli/'
exp_questions_path = './stimuli/ES_questions.csv'

# column name of trial type names in TrialSpecifications.csv
trialspec_col = 'trial_type'

# task instruction
instr_txt = './instructions/exp_instr_es.txt'

# wait trigger screen
ready_txt = './instructions/wait_trigger.txt'


from psychopy import logging
from psychopy.platform_specific import win32
#from src.fileIO import write_csv, create_headers, load_conditions_dict
#from src.datastructure.stimulus import stimulus_onefeat, stimulus_ExpSample
#from src.datastructure.datastructure import *
#from src.datastructure import trial_library

from random import shuffle, randint, uniform, choice
from itertools import product


class ExpSample(object):
    '''
    generate a experience sampling trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details

    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, stimulus_generator, last_trial):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator
            the output of the generator is a list of dictionaries
            the header of the dictionaries are
            "Item", "Question", "Scale_low", "Scale_high"

        last_trial: dict
            the previous trial; some trials need this information
            if it's a experience sampling question,
            zero-back or no-go trial, None type is accepted

        output

        dict_rows: a list of dict
            a list of trials in dictionary

        trial_time: a list of float
            total time of each trial, for counter

        '''
        items = next(stimulus_generator.generate())

        dict_rows = []
        trial_time = []
        for item in items:

            dict_row = {key: None for key in self.lst_header}
            dict_row['TrialIndex'] = None
            dict_row['Condition'] = None

            dict_row['TrialType'] = self.trial_spec['trial_type']
            dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
            dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

            dict_row['stimPicLeft'] = item['Scale_low']
            dict_row['stimPicRight'] =  item['Scale_high']
            rand_marker_start = round(uniform(1, 10), 1)
            dict_row['Ans'] = str(rand_marker_start)

            dict_row['stimPicMid'] = item['Item']

            dict_rows.append(dict_row)
            trial_time.append(self.trial_spec['trial_t_total'])

        yield dict_rows, trial_time

class NoGo(object):
    '''
    generate a one back trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details

    '''
    def __init__(self, trial_spec, lst_header):

        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, stimulus_generator, last_trial):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        t: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}
        item_list = next(stimulus_generator.generate())

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'],self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = item_list[0]
        dict_row['stimPicRight'] = item_list[1]
        dict_row['stimPicMid'] = None
        dict_row['Ans'] = 'NA'

        yield dict_row, self.trial_spec['trial_t_total']



class ZeroBack(object):
    '''
    generate a zero back trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details

    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, stimulus_generator, last_trial):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}
        item_list = next(stimulus_generator.generate())

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'],self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = item_list[0]
        dict_row['stimPicRight'] = item_list[1]
        dict_row['Ans'] = choice(['left', 'right'])

        if dict_row['Ans'] == 'left':
            dict_row['stimPicMid'] = dict_row['stimPicLeft']
        else:
            dict_row['stimPicMid'] = dict_row['stimPicRight']

        yield dict_row,self.trial_spec['trial_t_total']


class OneBack(object):
    '''
    generate a one back recall trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details
    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, last_trial, stimulus_generator):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = '?'
        dict_row['stimPicRight'] = '?'

        dict_row['Ans'] = choice(['left', 'right'])

        if dict_row['Ans'] == 'left':
            dict_row['stimPicMid'] = last_trial['stimPicLeft']
        else:
            dict_row['stimPicMid'] = last_trial['stimPicRight']

        yield dict_row,self.trial_spec['trial_t_total']

class ZeroBackRecog(object):
    '''
    generate a zero back trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details

    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, stimulus_generator, last_trial):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}
        item_list = next(stimulus_generator.generate())

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'],self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = item_list[0]
        dict_row['stimPicRight'] = item_list[1]
        null = filter(lambda x: x not in item_list, stimulus_generator.stimuli)[0]

        dict_row['Ans'] = choice(['yes', 'no'])

        if dict_row['Ans'] == 'yes':
            dict_row['stimPicMid'] = choice(item_list)
        else:
            dict_row['stimPicMid'] = null

        yield dict_row,self.trial_spec['trial_t_total']


class OneBackRecog(object):
    '''
    generate a one back recall trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details
    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, last_trial, stimulus_generator):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary
        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}
        # create a equal chance to get a present/absent target in the pre trial
        item_list = [last_trial['stimPicLeft'], last_trial['stimPicRight']]


        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = '?'
        dict_row['stimPicRight'] = '?'

        null= filter(lambda x: x not in item_list, stimulus_generator.stimuli)[0]

        dict_row['Ans'] = choice(['yes', 'no'])

        if dict_row['Ans'] == 'yes':
            dict_row['stimPicMid'] = choice(item_list)
        else:
            dict_row['stimPicMid'] = null

        yield dict_row,self.trial_spec['trial_t_total']

class Recognition(object):
    '''
    generate a one back recognition trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details
    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, last_trial, stimulus_generator):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        # decide to preserve left or right
        for f1 in stimulus_generator.feature1:
            if f1 not in [last_trial['stimPicLeft'][0], last_trial['stimPicRight'][0]]:
                distract_feature1 = f1
        for f2 in stimulus_generator.feature2:
            if f2 not in [last_trial['stimPicLeft'][1], last_trial['stimPicRight'][1]]:
                distract_feature2 = f2
        distractor = (distract_feature1, distract_feature2)

        if choice(['left', 'right']) == 'left':
            dict_row['stimPicLeft'] = last_trial['stimPicLeft']
            dict_row['stimPicRight'] = distractor
            dict_row['stimPicMid'] = '?'
            dict_row['Ans'] = 'yes'

        else:
            dict_row['stimPicLeft'] = distractor
            dict_row['stimPicRight'] = last_trial['stimPicRight']
            dict_row['stimPicMid'] = '?'
            dict_row['Ans'] = 'no'
        yield dict_row,self.trial_spec['trial_t_total']


class ZeroBack_feature(object):
    '''
    generate a zero back trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details
    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, stimulus_generator, last_trial):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}
        item_list = next(stimulus_generator.generate())

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = item_list[0]
        dict_row['stimPicRight'] = item_list[1]

        target_item = choice(item_list)
        target_feat = choice(target_item)

        # decide to preserve left or right
        # they all the items on screen can only share on feature
        if target_feat in stimulus_generator.feature1:
            for f2 in stimulus_generator.feature2:
                if f2 not in [dict_row['stimPicLeft'][1], dict_row['stimPicRight'][1]]:
                    distract_feature2 = f2
            dict_row['stimPicMid'] = (target_feat, distract_feature2)
        else:
            for f1 in stimulus_generator.feature1:
                if f1 not in [dict_row['stimPicLeft'][0], dict_row['stimPicRight'][0]]:
                    distract_feature1 = f1
            dict_row['stimPicMid'] = (distract_feature1, target_feat)

        if dict_row['stimPicLeft'] == target_item:
            dict_row['Ans'] = 'left'
        else:
            dict_row['Ans'] = 'right'

        yield dict_row,self.trial_spec['trial_t_total']


class OneBack_feature(object):
    '''
    generate a one back trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details
    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, last_trial, stimulus_generator):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator
        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary
        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']

        dict_row['stimPicLeft'] = '?'
        dict_row['stimPicRight'] = '?'

        target_item = choice([last_trial['stimPicLeft'], last_trial['stimPicRight']])
        target_feat = choice(target_item)
        # decide to preserve left or right

        if target_feat in stimulus_generator.feature1:
            for f2 in stimulus_generator.feature2:
                if f2 not in [last_trial['stimPicLeft'][1], last_trial['stimPicRight'][1]]:
                    distract_feature2 = f2
            dict_row['stimPicMid'] = (target_feat, distract_feature2)

        else:
            for f1 in stimulus_generator.feature1:
                if f1 not in [last_trial['stimPicLeft'][0], last_trial['stimPicRight'][0]]:
                    distract_feature1 = f1
            dict_row['stimPicMid'] = (distract_feature1, target_feat)

        if last_trial['stimPicLeft'] == target_item:
            dict_row['Ans'] = 'left'
        else:
            dict_row['Ans'] = 'right'

        yield dict_row,self.trial_spec['trial_t_total']


class Recognition_feature(object):
    '''
    generate a one back trial detail

    trial_spec: dict
        trial specification

    lst_header: list
        headers for generating dictionary to store trial details

    '''
    def __init__(self, trial_spec, lst_header):
        self.trial_spec = trial_spec
        self.lst_header = lst_header

    def generate_trial(self, last_trial, stimulus_generator):
        '''
        a generater that creates trials

        stimulus_generator: generator
            stimulus generator

        last_trial: dict
            the previous trial; some trials need this information
            if it's a zero-back or no-go trial, None type is accepted

        output

        dict_row: dict
            a trail in dictionary

        self.trial_spec['trial_t_total']: float
            total time of this trial, for counter

        '''
        dict_row = {key: None for key in self.lst_header}

        dict_row['TrialIndex'] = None
        dict_row['Condition'] = None

        dict_row['TrialType'] = self.trial_spec['trial_type']
        dict_row['fix_duration'] = uniform(self.trial_spec['fix_t_min'], self.trial_spec['fix_t_max'])
        dict_row['stim_duration'] =self.trial_spec['trial_t_total'] - dict_row['fix_duration']
        # decide to preserve left or right
        for f1 in stimulus_generator.feature1:
            if f1 not in [last_trial['stimPicLeft'][0], last_trial['stimPicRight'][0]]:
                distract_feature1 = f1
        for f2 in stimulus_generator.feature2:
            if f2 not in [last_trial['stimPicLeft'][1], last_trial['stimPicRight'][1]]:
                distract_feature2 = f2
        distractor = (distract_feature1, distract_feature2)

        if choice(['left', 'right']) == 'left':

            target_item = last_trial['stimPicLeft']
            target_feat = choice(target_item)

            if target_feat in stimulus_generator.feature1:
                dict_row['stimPicLeft'] = (target_feat, last_trial['stimPicRight'][1])

            else:
                dict_row['stimPicLeft'] = (last_trial['stimPicRight'][0], target_feat)

            dict_row['stimPicRight'] = distractor
            dict_row['stimPicMid'] = '?'
            dict_row['Ans'] = 'left'

        else:
            target_item = last_trial['stimPicRight']
            target_feat = choice(target_item)

            if target_feat in stimulus_generator.feature1:
                dict_row['stimPicRight'] = (target_feat, last_trial['stimPicLeft'][1])

            else:
                dict_row['stimPicRight'] = (last_trial['stimPicLeft'][0], target_feat)

            dict_row['stimPicLeft'] = distractor
            dict_row['stimPicMid'] = '?'
            dict_row['Ans'] = 'right'

        yield dict_row,self.trial_spec['trial_t_total']


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


class stimulus_twofeat(object):
    '''
    double feature stimulus generator

    save features and genenrate stimuli pair

    feature1, feature2 : list, features of stimulus

    '''
    def __init__(self, feature1, feature2):
        self.feature1 = feature1
        self.feature2 = feature2

    def generate(self):
        '''
        generate a pair of stimuli with no shared feature

        '''
        shuffle(self.feature1)
        shuffle(self.feature2)
        item_left = (self.feature1[0], self.feature2[0])
        item_right = (self.feature1[1], self.feature2[1])

        yield [item_left, item_right]


class stimulus_twofeat_mix(object):
    '''
    double feature stimulus generator with mixed congurency
    The stimulis pair can share one feature or no feature.

    save features and genenrate stimuli pair

    feature1, feature2 : list, features of stimulus

    '''
    def __init__(self, feature1, feature2):
        self.feature1 = feature1
        self.feature2 = feature2
        self.stimuli = list(product(self.feature1, self.feature2))

    def generate(self):
        '''
        generate a pair of stimuli

        '''
        shuffle(self.stimuli)
        item_left = self.stimuli[0]
        item_right = self.stimuli[1]

        yield [item_left, item_right]


class stimulus_onefeat(object):
    '''
    single feature stimulus generator

    save features and genenrate stimuli
    features: list, features of stimuli

    '''
    def __init__(self, features):
        self.stimuli = features

    def generate(self):
        '''
        generate a pair of stimuli with no shared features

        '''

        shuffle(self.stimuli)
        yield [self.stimuli[0], self.stimuli[1]]


def tup2str(dir_path, tuple_stim, filesuffix):
    '''
    trun tuple to a string (filename)
    the filename must look like:
        feature1_feature2.png

    dir_path: str
        example: './stimulus/'

    tuple_stim: tuple
        stimulus, ('feature1', 'feature2')

    filesuffix: str
        expample '.png'

    return
        str, example: './stimulus/feature1_feature2.png'
    '''
    return dir_path + ('_').join(tuple_stim) + filesuffix


class experiment_parameters(object):
    '''
    save basic parameter, late pass to trial_builder

    block_length: float
        the length of a condition block, must be 1.5 * n

        default as 1.5 minutes

    block_go_n: int
        the number of catch trials (of any kind) in a block
        must be 6 * n
        default as 6

    runs: int
        the number of time to go through a set of conditions

    '''
    def __init__(self, block_length=1.5, block_go_n=6, runs=1):
        self.block_length = block_length
        self.block_go_n = block_go_n
        self.blocks = []
        self.conditions = []
        self.headers = None
        self.runs = runs

    def load_conditions(self, condition_path):
        '''

        load all the conditions for building a block

        condition_path
            path to the condition file
        '''

        conditions, _ = load_conditions_dict(condition_path)

        # conditions = []
        # with codecs.open(condition_path, 'r', encoding='utf8') as f:
        #     reader = csv.reader(f)
        #     for cond in reader:
        #         conditions.append(cond[0])
        self.conditions = conditions

    def load_header(self, trialheader_path):
        _, header = load_conditions_dict(trialheader_path)
        self.headers = header

    def create_counter(self):
        '''
        create:
        a counter in seconds for task length
        a list of counters for the number of catch trial type 1 to n
       '''
        time = self.block_length * 60
        trial_library_n = len(self.conditions[0]) - 1
        go_n = [self.block_go_n / trial_library_n] * trial_library_n
        return time, go_n


class trial_finder(object):
    '''
    find and create trials accroding to the trial specification
    later pass to trial_bulder

    trialspec_path: a path to the trial specification file
    trialspec_col: the column name directing to the trial specification info

    '''
    def __init__(self, trialspec_path, trialspec_col):
        self.trialspec_path = trialspec_path
        self.trialspec_col = trialspec_col

    def get(self, trial_type):
        '''
        get the trial by keyword 'trial_type'
        only the supporting ones works!

        trial_type: str

        '''
        with codecs.open(self.trialspec_path, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            #loop through csv list
            for row in reader:

                # first convert strings to float
                for item in row.keys():
                    row[item] = str2float(row[item])

                # if current rows trial type is equal to input, print that row
                if trial_type == row[self.trialspec_col]:
                    trial_spec = row
                    trial_mod = getattr(trial_library, trial_type)
                    return trial_mod(trial_spec=trial_spec, lst_header=None)

                else:
                    pass


class trial_builder(object):
    '''
    build trials for each run
    need these -
        experiment_parameters: obj
            store experiment parameter

        trial_finder: obj
            it finds a trial generator for you

        stimulus_generator: obj
            it generate stimulus pair
    '''
    def __init__(self):
        self.trial_index = 0
        self.dict_trials = []
        self.last_trial = None
        self.init_trial_index = 0

    def initialise(self, task_t, go_n):
        '''
        clean the buffer and reset counter

        task_t: float
            the length of the block in second
        go_n: list, int
            a list of number of catch trials
        '''
        self.dict_trials = []
        self.task_t = task_t
        self.go_n = go_n
        self.last_trial = None
        self.trial_index = self.init_trial_index


    def block_trials(self, trial_finder, block, trial_headers):

        '''
        trial_finder: object
            it finds what type of trial you need based on a string

        block: str
            the name of the current block

        trial_headers: lst
            the trial headers

        return
            objects
        '''

        trial_NoGo = trial_finder.get(trial_type='NoGo')
        trial_NoGo.lst_header = trial_headers

        trial_Go1 = trial_finder.get(trial_type=block['GoTrial1'])
        trial_Go1.lst_header = trial_headers

        trial_Go2 = trial_finder.get(trial_type=block['GoTrial2'])
        trial_Go2.lst_header = trial_headers

        trial_Go = [trial_Go1, trial_Go2]

        return trial_NoGo, trial_Go

    def get_n_NoGo(self, trial_NoGo):
        '''
        generate a random number of no-go trials

        trial_NoGo: object
            the no-go trial object. only this object contains the information for this

        retrun
            int
        '''

        n_min = int(trial_NoGo.trial_spec['trial_n_min'])
        n_max = int(trial_NoGo.trial_spec['trial_n_max']) + 1

        return randrange(n_min, n_max, 1)

    def save_trial(self, cur_trial, block):
        '''
        save the trial to the temporary list

        cur_trial: dict
            a trial in dictionary form

        block: str
            the current block name

        '''
        cur_trial['Condition'] = block
        cur_trial['TrialIndex'] = self.trial_index
        self.trial_index += 1
        self.dict_trials.append(cur_trial)
        self.last_trial = cur_trial

    def build(self, experiment_parameters, trial_finder, \
              stimulus_generator, expsampling_generator, block):
        '''
        build the trial generator

        experiment_parameters: obj
            store experiment parameter

        trial_finder: obj
            it finds a trial generator for you

        stimulus_generator: obj
            it generate stimulus pair

        block: string or None
            indicate the task condiiton in the first block
            Options are '0', '1', or None (random start)

        '''
        for cur in range(experiment_parameters.runs):

            # load condtions
            blocks = experiment_parameters.conditions.copy()
            # initialize the output storage and the counter
            run  = []
            trial_idx_tmp = 0

            init_task_t, init_go_n = experiment_parameters.create_counter()

            for block in blocks:
                self.initialise(init_task_t, init_go_n)

                # get the specific go trials according to the block you are in
                trial_NoGo, trial_Go = self.block_trials(
                        trial_finder, block, experiment_parameters.headers)
                self.trial_index = trial_idx_tmp

                while self.task_t != 0: # start counting
                    for i in range(experiment_parameters.block_go_n):
                        # get no-go trial number
                        n_NoGo = self.get_n_NoGo(trial_NoGo)

                        # genenrate the no-go trials before the go trial occur
                        for j in range(n_NoGo):
                            cur_trial, t = next(trial_NoGo.generate_trial(
                                stimulus_generator=stimulus_generator,
                                last_trial=self.last_trial))
                            self.task_t -= t
                            self.save_trial(cur_trial, block['Condition'])

                        # generate the go trial
                        # go trial: type 1 or type 2
                        # see which go trial type were all used
                        use_go = [i for i, e in enumerate(self.go_n) if e > 0]
                        if use_go:
                            # select a random one from the available ones
                            idx = choice(use_go)


                        if trial_Go[idx].__class__.__name__=='ExpSample':
                            # if it's experience sampling
                            cur_trial, t = next(trial_Go[idx].generate_trial(
                            stimulus_generator=expsampling_generator,
                            last_trial=self.last_trial)) # n-back
                            for trial in cur_trial:
                                self.task_t -= t[0]
                                self.save_trial(trial, block['Condition'])
                        else:
                            cur_trial, t = next(trial_Go[idx].generate_trial(
                            stimulus_generator=stimulus_generator,
                            last_trial=self.last_trial)) # n-back

                            self.task_t -= t
                            self.save_trial(cur_trial, block['Condition'])


                    # add 1~ 2 no-go trials and then a switch screen to end this block
                    for k in range(randrange(1, 3, 1)):
                        cur_trial, t = next(trial_NoGo.generate_trial(
                                    stimulus_generator=stimulus_generator,
                                    last_trial=self.last_trial))
                        self.task_t -= t
                        self.save_trial(cur_trial, block['Condition'])

                    cur_trial, t = next(trial_NoGo.generate_trial(
                        stimulus_generator=stimulus_generator,
                        last_trial=self.last_trial))
                    cur_trial['TrialType'] = 'Switch'
                    cur_trial['stimPicMid'] = 'SWITCH'
                    cur_trial['stimPicLeft'] = None
                    cur_trial['stimPicRight'] = None

                    self.save_trial(cur_trial, 'Switch')
                    if self.task_t != 0:
                        # if this list of trials is not good for the block, restart
                        init_task_t, init_go_n = experiment_parameters.create_counter()
                        self.initialise(init_task_t, init_go_n)
                        self.trial_index = trial_idx_tmp
                    else:
                        # if it's good save this block to the run
                        print('save this block')
                        run += self.dict_trials
                        trial_idx_tmp = self.trial_index
            yield run



def str2float(string):
    '''
    detect if the string can be converted to float.
    if so, return the converted result
    else, return the input string
    '''
    try:
        return float(string)
    except ValueError:
        return string

# Base settings that apply to all environments.
# These settings can be overwritten by any of the
# environment settings.

BASE = {
    'test': False,
    'mouse_visible': False,
    'logging_level': logging.INFO
}


# Development environment settings. Used for testing,
# outside of the MR room.
DEV = {
    'env': 'dev',
    'test': True,
    'window_size': (800, 600),
    'logging_level': logging.DEBUG
}

# Production settings
PRODUCTION = {
    'test': False,
    'logging_level': logging.EXP
}

# Laboratory setting
# LAB = {
#     'env': 'lab',  # Enviroment name
#     'window_size': 'full_screen',
#     'input_method': 'keyboard'
#     }

LAB = {
    'env': 'lab',  # Enviroment name
    'window_size': (1280,800),
    'input_method': 'keyboard'
    }



# # Development environment settings. Used for testing,
# # outside of the MR room.
# DEV = {
#     'env': 'dev',  # Enviroment name
#     'window_size': (800, 600),
#     'button_box': None,  # No button box

#     # Number of runs
#     'n_runs': 1,

#     # Rating scale descriptions
#     'gaze_desc': "Left                   \
#                                         Right",
#     'self_desc': "Very Negative                   \
#                                         Very Positive",
#     'other_desc': "Very Negative                   \
#                                         Very Positive",
# }

MRI = {
    'env': 'mri',
    'window_size': 'full_screen',
    'input_method': 'serial',
}

# experiment specific version related setting
VER_A = {
        'rec_color': 'blue',
        'loc_color': 'red',
        'rec_keys': ['z', 'x'],
        'loc_keys': ['n', 'm'],
        'rec_keyans': ['yes', 'no'],
        'loc_keyans': ['left', 'right']
        }

VER_B = {
        'rec_color': 'red',
        'loc_color': 'blue',
        'rec_keys': ['n', 'm'],
        'loc_keys': ['z', 'x'],
        'rec_keyans': ['yes', 'no'],
        'loc_keyans': ['left', 'right']
        }

VER_A_MRI = {
            'rec_keys': ['1', '2'],
            'loc_keys': ['6', '7']
            }

VER_B_MRI = {
            'rec_keys': ['6', '7'],
            'loc_keys': ['1', '2']
            }

EXP_SAMPLING_A = {
        '0_back_color': 'blue',
        '1_back_color': 'red',
        'loc_keys': ['1', '2'],
        'loc_keyans': ['left', 'right']
        }

EXP_SAMPLING_B = {
        '0_back_color': 'red',
        '1_back_color': 'blue',
        'loc_keys': ['1', '2'],
        'loc_keyans': ['left', 'right']
        }

def get_trial_generator(block):
    '''
    return a trial generator and a list of data log headers
    '''
    # now define the generators
    # create experiment parameters
    if block == "0":
        condition_path = './parameters/ConditionsSpecifications_ES_zeroback.csv'
    elif block == "1":
        condition_path = './parameters/ConditionsSpecifications_ES_oneback.csv'

    parameters = experiment_parameters(
            block_length=BLOCK_TIME, block_go_n=BLOCK_GO_N, runs=1)
    parameters.load_conditions(condition_path)
    parameters.load_header(trialheader_path)
    questions, _ = load_conditions_dict('./stimuli/ES_questions.csv')


    # create trial finder
    find_trial = trial_finder(trialspec_path=trialspec_path, trialspec_col=trialspec_col)

    # create stimulus generators
    # stimulus_generator = stimulus_twofeat(feature1=shape, feature2=texture)
    stimulus_generator = stimulus_onefeat(features=shape)
    exp_sample_generator = stimulus_ExpSample(questions)
    # now build the trials
    builder = trial_builder()
    # build the trial generator
    trial_generator = builder.build(parameters, find_trial, stimulus_generator, exp_sample_generator, block)

    return trial_generator, parameters.headers


def get_settings(env, ver, test=False):
    '''Return a dictionary of settings based on
    the specified environment, given by the parameter
    env. Can also specify whether or not to use testing settings.

    Include keypress counter balancing
    '''
    # Start with the base settings
    settings = BASE

    # display and key press counter balancing
    if ver == 'A':
        settings.update(EXP_SAMPLING_A)
    elif ver == 'B':
        settings.update(EXP_SAMPLING_B)
    else:
        raise ValueError('Version "{0}" not supported.'.format(ver))

    if env == 'lab':
        settings.update(LAB)
    # elif env == 'dev':
    #     settings.update(DEV)
    elif env == 'mri':
        settings.update(MRI)

    else:
        raise ValueError('Environment "{0}" not supported.'.format(env))

    # Update it with either the test or production settings

    if test:
        settings.update(TEST)
    else:
        settings.update(PRODUCTION)

    return settings

from src.datastructure.stimulus import tup2str

def parse_stimulus_name(trial):
    '''
    parse tuples to proper file names
    '''
    for key in trial.keys():
        if type(trial[key]) is tuple:
            trial[key] = tup2str(stimulus_dir, trial[key], '.png')
        elif 'stimPic' in key and type(trial[key]) is str:
            if trial[key] in shape:
                trial[key] = stimulus_dir + trial[key] + '.png'
    return trial
