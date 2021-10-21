#Written by Brontë McKeown and Theodoros Karapanagiotidis
from psychopy import visual 
from psychopy import visual 
from psychopy import gui, data, core,event
import csv
import time
from time import localtime, strftime, gmtime
from datetime import datetime
import os.path
import pyglet 
import pandas as pd
from itertools import groupby

############### Section for filmlist randomisation ################################################

# read in filmlist csv which is sorted according to condition (cert and uncert)
df = pd.read_csv('csv\\sorted_filmList.csv')

# separate the dataframe into conditions (cert and uncert)
cert = df['cert']
uncert = df['uncert']

def randomisation(df1,df2):
    """Returns randomised list for 1st dataframe given
    1st film is always determined by condition required
    The remaining films are randomly presented but there are never more
    than two consecutive conditions"""
    max_count = 1


    while max_count == 1:
        x_bad = []
        # randomly select one film from each condition which will go first in the list
        x_1 = df1.sample(n=1)
        
        # drop the randomly selected films from each condition list
        x_cert = df1.drop(x_1.keys()[0])
        
        # put together remaining lists minus each film already taken out for a and b
        # randomise these lists
        x_remaining = pd.concat([x_cert,df2])
        x_random = x_remaining.sample(n=7)
        
        # put together first item of a list with rest of randomised a list
        x_complete = pd.concat([x_1,x_random])
        
        # rest indices so that the final a and b lists can be put together to write to 
        # csv file
        x_final = x_complete.reset_index(drop= True)
        
        # convert dataframe to list
        x_list = x_final.values.tolist()
        
        # only retain cert and uncert from filename
        for i in range(len(x_list)):
            x_list[i] = x_list[i].split('/')[1].split('_')[0]
        
        # checks how many times condition is placed consecutively 
        x_check = [[i, sum(1 for i in group)] for i, group in groupby(x_list)]

        # check if any condition appears > twice consecutively in x_check list.
        if any(i[1] > 2 for i in x_check):
            #print (x_check)
            # if any condition appears > twice consecutively, continues loop.
            print ('Conditions not met, reshuffling.')
        else:
            # if conditions don't appear > twice consecutively, breaks loop.
            #print (x_check)
            print ('Conditions met, finished.')
            max_count = 0
    return x_final

# call randomisation function for a and b lists
a_final = randomisation(cert,uncert)
b_final = randomisation(uncert,cert)

# put together final a and b lists to write to csv file
df_final = pd.concat([a_final,b_final],axis = 1)

# rename column headers to be a and b instead of 0 and 1
df_final.columns=['a','b']

# save a and b lists concatanated to csv file without indexes
df_final.to_csv('csv\\filmList.csv', index = False)

###################################################################################################

# kill switch for Psychopy3
event.globalKeys.clear() # clear global keys 
esc_key= 'escape' # create global key for escape
# define function to quit programme
def quit():
    print ('User exited')
    win.close()
    core.quit()
# call globalKeys so that whenever user presses escape, quit function called
event.globalKeys.add(key=esc_key, func=quit)

# user should set cwd to the experiment directory.
os.chdir('R:\\Task_SGT\\Bronte\\movie_study_2.0')
# user should set directory for output files to be stored. 
save_path= 'R:\\Task_SGT\\Bronte\\movie_study_2.0\\output\\questionnaire'

# user can update instructions for task here if required.
instructions = """You will be presented with several video clips. These clips are rated 15 and contain extreme violence, aggression and bad language. If you find these types of clips distressing, please do not participate in this study. 
\nIf at any point, you become distressed and would like to stop the task, please inform the experimenter. You will not be penalised for withdrawing from the study. 
\nAt the end of each task block, you will be asked to rate several statements about the ongoing thoughts you experienced during that block. 
\nTo rate these statements, hold 1 to move the marker left along the slider and hold 2 to move the marker right along the slider. When you are happy with your selection, please press 4 to move on to the next statement. 
\nPress 1 to begin the experiment."""

# user can update start screen text here if required. 
start_screen = "The experiment is about to start. Press 5 to continue."

# user can edit headers for output csv file here. 
fieldnames = ['Participant_number', 'videoName','Condition','Video_startTime','Video_endTime','Questionnaire_startTime','Questionnaire_endTime',
'TrialDuration','Focus','Future','Past','Self','Other','Emotion','Modality','Detailed','Deliberate','Problem','Diversity','Intrusive','Source', 'Arousal', 'Tense','Uncertainty'] 

# create a dictionary to store information from the dialogue box.
inputbox = {'expdate': datetime.now().strftime('%Y%m%d_%H%M'),'part_number':'','videoCondition':['a','b']}
# create dialogue box.
# user enters participant number + video condition (i.e. the Header of the column of video lists in the film csvFile).
dlg=gui.DlgFromDict(inputbox, title = 'Input participation info',
                  	fixed='expdate',
                  	order=['expdate', 'part_number','videoCondition'])

# if the user doesn't press ok, the programme will quit and inform user.
if not dlg.OK:
	print ("User exited")
	core.quit()

def thought_probes (video_name, participant_number, last=0):
    """Presents thought probes, stores responses and presents break screens in between videos and end screen if it is the last trial"""

    # use trialhandler to present task, arousal and uncertainty questions from csv file in sequential order. 
    fixedQuestions = data.TrialHandler(nReps = 1, method = 'sequential', trialList = data.importConditions('references/fixedQuestions.csv'), name = 'fixedQuestions')

    # use trialhandler to present the remaining thought probes from csv file in random order. 
    Questionnaire = data.TrialHandler(nReps = 1, method = 'random', trialList = data.importConditions('references/questions.csv'), name = 'Questionnaire')

    # create rating scale for user to rate thought probes.
    ratingScale = visual.RatingScale(win, low=0, high=10, markerStart=5.0,
                precision=10,
                leftKeys='1', rightKeys='2', acceptKeys='4', scale = None, labels = None, acceptPreText = 'Press key', tickMarks = [1,10])

    # create text stimulus for thought probe presentation. 
    QuestionText = visual.TextStim(win, color = [-1,-1,-1], alignHoriz = 'center', alignVert= 'top', pos =(0.0, 0.3))
    # create text stimuli for low and high scale responses. 
    Scale_low = visual.TextStim(win, pos= (-0.5,-0.5), color ='black')
    Scale_high = visual.TextStim(win, pos =(0.6, -0.5), color ='black')

    # make thisRunDict global so that it can be accessed outside of function to write to outputfile. 
    global thisRunDict 
    # store participant number and video name in thisRunDict to write to outputfile.  
    thisRunDict= {'Participant_number': str(participant_number),'videoName': video_name }

    # loop through each thought probe in the fixedQuestions created above using trialhandler.
    for question in fixedQuestions:
        ratingScale.noResponse = True

        # section for keyboard handling. 
        key = pyglet.window.key
        keyState = key.KeyStateHandler()
        win.winHandle.activate() # to resolve mouse click issue. 
        win.winHandle.push_handlers(keyState)
        pos = ratingScale.markerStart
        inc = 0.1 

        # while there is no response from user, present thought probe and scale.
        while ratingScale.noResponse:

            # use 1 and 2 keys to move left and right along scale. 
            if keyState[key._1] is True:
                pos -= inc
            elif keyState[key._2] is True:
                pos += inc
            if pos > 10: 
                pos = 10
            elif pos < 1:
                pos = 1
            ratingScale.setMarkerPos(pos)

            # set text of probe and responses 
            QuestionText.setText(question['Questions'])
            Scale_low.setText(question['Scale_low'])
            Scale_high.setText(question['Scale_high'])

            # draw text stimuli and rating scale
            QuestionText.draw()
            ratingScale.draw() 
            Scale_low.draw()
            Scale_high.draw()

            # store response using getRating function
            responded = ratingScale.getRating()
            win.flip()

        # reset marker to middle of scale each time probe is presented. 
        ratingScale.setMarkerPos((0.5))
        
        # for each probe, store probe label and response in thisRunDict. 
        thisRunDict[ str(question['Label'] )] = str(responded)


    # loop through each thought probe in the Questionnaire created above using trialhandler.
    for question in Questionnaire:
        ratingScale.noResponse = True

        # section for keyboard handling. 
        key = pyglet.window.key
        keyState = key.KeyStateHandler()
        win.winHandle.activate() # to resolve mouse click issue. 
        win.winHandle.push_handlers(keyState)
        pos = ratingScale.markerStart
        inc = 0.1 

        # while there is no response from user, present thought probe and scale.
        while ratingScale.noResponse:

            # use 1 and 2 keys to move left and right along scale. 
            if keyState[key._1] is True:
                pos -= inc
            elif keyState[key._2] is True:
                pos += inc
            if pos > 10: 
                pos = 10
            elif pos < 1:
                pos = 1
            ratingScale.setMarkerPos(pos)

            # set text of probe and responses 
            QuestionText.setText(question['Questions'])
            Scale_low.setText(question['Scale_low'])
            Scale_high.setText(question['Scale_high'])

            # draw text stimuli and rating scale.
            QuestionText.draw()
            ratingScale.draw() 
            Scale_low.draw()
            Scale_high.draw()

            # store response using getRating function.
            responded = ratingScale.getRating()
            win.flip()

        # reset marker to middle of scale each time probe is presented. 
        ratingScale.setMarkerPos((0.5))

        # for each probe, store probe label and response in thisRunDict. 
        thisRunDict[ str(question['Label'] )] = str(responded)
    
    # store when the questions end to later store in outputfile, this qEnd uses clock created at start of experiment. 
    qEnd = tasktime.getTime()
    # store trial end time for later use in calculating trial duration. 
    end =time.time()
    # calculate trial duration to store in outputfile. 
    trial_duration = (end-start)

    # sorts film by condition and saves condition of film to thisRunDict to save in outputfile 
    if 'uncert_' in film[videoCondition]:
        thisRunDict['Condition'] = str('uncert')
    elif 'cert_' in film[videoCondition]:
        thisRunDict['Condition'] = str('cert')

    # add timings to global thisRunDict to write to outputfile below.
    thisRunDict['Video_startTime']= str(videoStart)
    thisRunDict['Video_endTime']= str(videoEnd)
    thisRunDict['Questionnaire_startTime']= str(videoEnd)
    thisRunDict['Questionnaire_endTime']= str(qEnd)
    thisRunDict['TrialDuration'] = str(trial_duration)

    # write responses and timings stored in thisRunDict to outputfile. 
    writer.writerows([thisRunDict])

    # create text stimuli to be updated for breaks and end screen. 
    stim = visual.TextStim(win, "", color = [-1,-1,-1], wrapWidth = 1300, units = "pix", height=40)

    # present break screen at the end of each set of questions.
    if last==0:
        print ('break')
        stim.setText("""You are welcome to take a break if you need to.
        \nIf you are feeling too distressed to continue with the task, please let the experimenter know. 
        \nIf you are happy to continue, press return when you are ready.""")
        stim.draw()
        win.flip()
        # Wait for user to press Return to continue. 
        key = event.waitKeys(keyList=(['return']), timeStamped = True)

    else:
        print ('end')
        # present end screen at the end of task. 
        stim.setText("""You have reached the end of the task.   
        \nThank you for your participation. 
        \nPress ENTER to exit the programme. Let the experimenter know that you have finished.""")
        stim.draw()
        win.flip()
        # wait for user to press escape to exit experiment. 
        key = event.waitKeys(keyList=(['return']), timeStamped = True)

# store participant number, video condition and experiment date provided by user in input box as variables for later use. 
part_number = inputbox['part_number']
videoCondition = inputbox['videoCondition']
expdate = inputbox['expdate']

# create filename based on user input. 
filename = '{}_{}_{}_{}.csv'.format(part_number, expdate,videoCondition,'scary')
# update filename to include absolute path so that it is stored in output directory. 
completeName = os.path.join(save_path, filename)
# open file for writing. 
outputfile = open(completeName, "w", newline = '')

# create variable which calls DictWriter to write to outputfile and specifies fieldnames.
writer = csv.DictWriter(outputfile, fieldnames)
# writes headers using fieldnames as specified above when creating writer variable.
writer.writeheader()

# use trialhandler to sequentially present films listed in filmlist csv file. 
filmDict = data.TrialHandler(nReps = 1, method = 'sequential', trialList = data.importConditions('references/filmList.csv'), name = 'filmList') 

# create white window for stimuli to be presented on throughout task. 
win = visual.Window(size=[1024, 768], color=[1,1,1,], monitor="testMonitor", fullscr= True, allowGUI = False)
# create text stimuli to be updated for start screen instructions.
stim = visual.TextStim(win, "", color = [-1,-1,-1], wrapWidth = 1300, units = "pix", height=40)

# update text stim to include instructions for task. 
stim.setText(instructions)
stim.draw()
win.flip()
# Wait for user to press 1 to continue. 
key = event.waitKeys(keyList=(['1']), timeStamped = True)

# update text stim to include start screen for task. 
stim.setText(start_screen)
stim.draw()
win.flip()
# Wait for user to press 5 to continue. 
key = event.waitKeys(keyList=(['5']), timeStamped = True)
 
# start a clock right before the experiment starts
tasktime = core.Clock()
tasktime.reset()

# loop through each film stored in filmDict created above using trialhandler. 
for film in filmDict:
    # store trial start time for later use in calculating trial duration. 
    start =time.time()

    # store when the video started to later store in outputfile, this videoStart uses clock created at start of experiment. 
    videoStart = tasktime.getTime()

    # present film using moviestim3
    mov = visual.MovieStim3 (win, film[videoCondition], size=(1920, 1080), flipVert=False, flipHoriz=False, loop=False)

    while mov.status != visual.FINISHED:
        mov.draw()
        win.flip()

    # store when the video ends to later store in outputfile, this videoEnd uses clock created at start of experiment. 
    videoEnd = tasktime.getTime()

    # If statement to either present break screen or end screen
    nextTrial = filmDict.getFutureTrial(n=1) # fixes error for end screen 
    if nextTrial is None or nextTrial[videoCondition] == None:
        # when the video has ended, call thought_probes function to present probes and rating scale
        thought_probes(film[videoCondition], part_number,1) 
    else:
        thought_probes(film[videoCondition], part_number)

    outputfile.flush()