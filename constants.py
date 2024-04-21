#data/device managing

SAMPLING_FREQ = 250     #mintavételi freq, ez stabil, írja, ha megváltozik, nem változtatni
RESIST_TIME = 10
EPOCH_LEN = 30         #30 s-nyi epochokkal dolgozik a yasa
YASA_INPUT_LEN = 2*60        #percben (az epoch 30 s)

#EEG metadata values

MALE = True
AGE = 22

#file managing

FILE_IDENTIFIER = "full_night_audio"
FILE_FOLDER_NAME = "C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files"

#audiofeedback

CHECK_LEN = 10
FREQUENCY_RIGHT = 250
FREQUENCY_LEFT = 253
W = 0.95
N3 = 0.5
TERMINATE = 780

#sleepstaging first wake hour file path

ONE_HOUR_WAKE = r"C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\one_hour_wake.pkl"

