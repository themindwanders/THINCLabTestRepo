
import os

cwd = os.path.dirname(os.path.abspath(__file__))  # Get the current working directory (cwd)
print(cwd)
os.chdir(cwd)

from . import ESQ, fingertappingTask,gonogoTask,memoryTask,otherTask,readingTask,selfTask
# import ESQ
# import fingertappingTask
# import gonogoTask
# import memoryTask
# import otherTask
# import readingTask
# import selfTask