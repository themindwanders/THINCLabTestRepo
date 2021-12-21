
import os
cwd = os.path.dirname(os.path.abspath(__file__))
print(cwd)
os.chdir(cwd)
from . import ESQ, fingertappingTask,gonogoTask,memoryTask,otherTask,readingTask,selfTask,zerobackTask,onebackTask,easymathTask,hardmathTask
