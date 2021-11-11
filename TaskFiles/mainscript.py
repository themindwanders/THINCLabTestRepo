#import semtask as sem
#import GoNoGo
#import FingTap as fing
#import ESQ
from psychopy import core, visual, gui
#import friendtask
import psychopy
import csv
#from TaskFiles.taskScripts.gonogoTask import main
#import ReadingMemory as rm
#import memoryTask as memtask
import taskScripts
import os
class metadatacollection():
        def __init__(self, INFO, main_log_location):
                self.INFO = INFO
                self.main_log_location = main_log_location
                self.sbINFO = "Test"
        def rungui(self):
                self.sbINFO = gui.DlgFromDict(self.INFO)
        def collect_metadata(self):  
                print(os.getcwd())
                if os.path.exists(self.main_log_location): 
                        os.remove(self.main_log_location)
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
        resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None, 'Response_Key':None, 'Auxillary Data': None}
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
        def __init__(self, task_module, main_log_location, backup_log_location,  name, numtrial, trialclass, runtime):
                self.main_log_location = main_log_location
                self.backup_log_location = backup_log_location
                self.task_module = task_module
                self.name = name
                self.numtrial = numtrial
                self.trialclass = trialclass
                self.runtime = runtime
        def run(self):
                if not os.path.exists(self.main_log_location):
                        if self.main_log_location.split(".")[1] == None:
                                os.mkdir(self.main_log_location.split("/")[0])
                        #if not self.main_log_location.split('.')[1] == ".csv" 
                        
                f = open(self.main_log_location, 'a')
                r = csv.writer(f)
                writer = csv.DictWriter(f, fieldnames=taskbattery.resultdict)
                r.writerow(["EXPERIMENT DATA:",self.name])
                r.writerow(["Start Time", taskbattery.time.getTime()])
                taskbattery.resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : self.name, 'Task Iteration': '1', 'Participant ID': self.trialclass[6], 'Response_Key' : None, 'Auxillary Data': None}
                self.task_module.runexp(self.backup_log_location, taskbattery.time, taskbattery.win, writer, taskbattery.resultdict, self.numtrial, self.runtime)
                f.close()
                taskbattery.resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None,'Response_Key':None, 'Auxillary Data': None}
import os

# Get the current working directory
cwd = os.path.dirname(os.path.abspath(__file__))  # Get the current working directory (cwd)

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
                'Number of Memory stimuli': '2',
                'Number of Zero-Back stimuli': '2',
                'Number of One-Back stimuli': '2',
                'Block Runtime': 10
                }
print(cwd)
datafile = str(os.getcwd() + '/log_file/testfull2.csv')

datafileBackup = 'log_file/testfullbackup.csv'
metacoll = metadatacollection(INFO, datafile)
metacoll.rungui()
metacoll.collect_metadata()
print(cwd)

ESQTask = task(taskScripts.ESQ, datafile, datafileBackup, "Experience Sampling Questions", 2, metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
friendTask = task(taskScripts.otherTask, datafile, datafileBackup, "Friend Task", int(metacoll.INFO['Number of "Other" stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
youTask = task(taskScripts.selfTask, datafile, datafileBackup, "You Task", int(metacoll.INFO['Number of "Self" stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
gonogoTask = task(taskScripts.gonogoTask, datafile, datafileBackup, "Go/NoGo Task", int(metacoll.INFO['Number of "Go/No Go" stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
fingertapTask = task(taskScripts.fingertappingTask, datafile, datafileBackup, "Finger Tapping Task", int(metacoll.INFO['Number of Finger Tapping blocks (5 stimuli per block)']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
readingTask = task(taskScripts.readingTask, datafile, datafileBackup, "Reading Task", int(metacoll.INFO['Number of Reading stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
memTask = task(taskScripts.memoryTask, datafile, datafileBackup,"Memory Task", int(metacoll.INFO['Number of Memory stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
zerobackTask = task(taskScripts.zerobackTask, datafile, datafileBackup,"Zero-Back Task", int(metacoll.INFO['Number of Zero-Back stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))
onebackTask = task(taskScripts.onebackTask, datafile, datafileBackup,"One-Back Task", int(metacoll.INFO['Number of One-Back stimuli']), metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']))

#tasks = list([friendTask,youTask,gonogoTask,fingertapTask,readingTask,memTask])
tasks = list([onebackTask])
tbt = taskbattery(tasks, ESQTask, INFO)



#readingTask.run()

tbt.run_battery()