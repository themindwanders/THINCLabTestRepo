#import task scripts here

from psychopy import core, visual
import psychopy
import csv




time = core.Clock()
win = visual.Window(size=(1280, 800),color='white', winType='pyglet')





# filename1 = 'log_file/testfull.csv'
# f = open(filename1, 'w')
# resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None}
# writer = csv.DictWriter(f, fieldnames=resultdict)
# writer.writeheader()