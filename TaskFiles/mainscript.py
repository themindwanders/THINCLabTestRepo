import semtask as sem
import GoNoGo
import FingTap as fing
import ESQ
from psychopy import core, visual, gui
import friendtask
import psychopy
import csv
import ReadingMemory as rm
import memoryTask as memtask

class metadatacollection():
        def __init__(self, INFO, main_log_location):
                self.INFO = INFO
                self.main_log_location = main_log_location
                self.sbINFO = "Test"
        def rungui(self):
                self.sbINFO = gui.DlgFromDict(self.INFO)
        def collect_metadata(self):  
                
                f = open(self.main_log_location, 'w')
                metawriter = csv.writer(f)
                metawriter.writerow(["METADATA:"])
                metawriter.writerow(self.sbINFO.inputFieldNames)
                metawriter.writerow(self.sbINFO.data)
                metawriter.writerow([taskbattery.time.getTime()])
                writer = csv.DictWriter(f, fieldnames=taskbattery.resultdict)
                writer.writeheader()
                f.close()
        
        

class taskbattery(metadatacollection):
        time = core.Clock()
        resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None}
        def __init__(self, tasklist, ESQtask, INFO):
                self.tasklist = tasklist
                self.ESQtask = ESQtask
                self.INFO = INFO

        win = visual.Window(size=(1280, 800),color='white', winType='pyglet')
        def run_battery(self):
                
                for i in self.tasklist:
                        i.run()
                        self.ESQtask.run()



class task(taskbattery,metadatacollection):
        def __init__(self, task_module, main_log_location, backup_log_location,  name, numtrial, trialclass):
                self.main_log_location = main_log_location
                self.backup_log_location = backup_log_location
                self.task_module = task_module
                self.name = name
                self.numtrial = numtrial
                self.trialclass = trialclass
        def run(self):
                f = open(self.main_log_location, 'a')
                r = csv.writer(f)
                writer = csv.DictWriter(f, fieldnames=taskbattery.resultdict)
                r.writerow(["EXPERIMENT DATA:",self.name])
                r.writerow(["Start Time", taskbattery.time.getTime()])
                taskbattery.resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : self.name, 'Task Iteration': '1', 'Participant ID': self.trialclass[6]}
                self.task_module.runexp(self.backup_log_location, taskbattery.time, taskbattery.win, writer, taskbattery.resultdict, self.numtrial)
                f.close()
                taskbattery.resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None}
import os

# Get the current working directory
cwd = os.path.dirname(os.path.abspath(__file__))  # Get the current working directory (cwd)
print(cwd)
os.chdir(cwd)  # Get all the files in that directory

INFO = {
                'Experiment Seed': '1',  # compulsory: name of program, used for trial definition in ./parameter/~.csv
                'Subject': '2',  # compulsory
                'Version': '2',  # counterbalance the fixation color
                'Number of "Self" stimuli': '2',
                'Number of "Other" stimuli': '2',
                'Number of "Go/No Go" stimuli': '2',
                'Number of Finger Tapping blocks (5 stimuli per block)': '2',
                'Number of Reading stimuli': '2',
                'Number of Memory stimuli': '2'
                }


metacoll = metadatacollection(INFO, 'log_file/testfull.csv')
metacoll.rungui()
metacoll.collect_metadata()


ESQTask = task(ESQ, 'log_file/testfull.csv', 'log_file/testfullbackup.csv', "Experience Sampling Questions", 2, metacoll.sbINFO.data)
friendTask = task(sem, 'log_file/testfull.csv', 'log_file/testfullbackup.csv', "Friend Task", int(metacoll.INFO['Number of "Other" stimuli']), metacoll.sbINFO.data)
youTask = task(friendtask, 'log_file/testfull.csv', 'log_file/testfullbackup.csv', "You Task", int(metacoll.INFO['Number of "Self" stimuli']), metacoll.sbINFO.data)
gonogoTask = task(GoNoGo, 'log_file/testfull.csv', 'log_file/testfullbackup.csv', "Go/NoGo Task", int(metacoll.INFO['Number of "Go/No Go" stimuli']), metacoll.sbINFO.data)
fingertapTask = task(fing, 'log_file/testfull.csv', 'log_file/testfullbackup.csv', "Finger Tapping Task", int(metacoll.INFO['Number of Finger Tapping blocks (5 stimuli per block)']), metacoll.sbINFO.data)
readingTask = task(rm, 'log_file/testfull.csv', 'log_file/testfullbackup.csv', "Reading Task", int(metacoll.INFO['Number of Reading stimuli']), metacoll.sbINFO.data)
memTask = task(memtask, 'log_file/testfull.csv','log_file/testfullbackup.csv',"Memory Task", int(metacoll.INFO['Number of Memory stimuli']), metacoll.sbINFO.data)
tasks = list([memTask, youTask,gonogoTask,fingertapTask,readingTask,friendTask])

tbt = taskbattery(tasks, ESQTask, INFO)



#readingTask.run()

tbt.run_battery()