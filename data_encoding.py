import os

#TODO: make it so that we are just reading from a txt file and then we can add it into a list here

mypath = '../../AI_dataset' #file that stores all data, should be in same directory as git repo
file = [os.path.join(mypath, f) for f in os.listdir(mypath) if not f.startswith('.')] #gets name of all 3 datafile, ignores .DS_Store file
file.sort()
key = range(1, 4)

data_encodings = dict(zip(key, file))
