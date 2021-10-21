from psychopy.misc import fromFile
# (replace with the file path to your .psydat file)
fpath = 'Basic_fMRI_Test_programs\data\Test1_2021_Sep_14_2123.psydat'
# load in the data
psydata = fromFile(fpath)
# (replace with the file path to where you want the resulting .csv
# to be saved)
save_path = 'test.csv'
# save the data as a .csv file, ie separating the values with a
# comma. 'CSV' simply means 'comma-separated values'
psydata.saveAsWideText(save_path, delim=',')