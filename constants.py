#data/device managing

SAMPLING_FREQ = 250     #mintavételi freq, ez stabil, írja, ha megváltozik, nem változtatni
SIGNAL_TIME = 350       #ha időre fut a kód, akkor a start signal után az input() helyére sleep(...)
RESIST_TIME = 5
EPOCH_LEN = 30         #30 s-nyi epochokkal dolgozik
YASA_INPUT_LEN = 2*60*7        #percben (az epoch 30 s)

#EEG metadata values

MALE = True
AGE = 22

#file managing

FILE_IDENTIFIER = "full_night_full_time"
FILE_FOLDER_NAME = "C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files"
SHOW_FEEDBACK = True

#audiofeedback decision

CHECK_LEN = 3

