#data/device managing

SAMPLING_FREQ = 250     #mintavételi freq, ez stabil, írja, ha megváltozik, nem változtatni
SIGNAL_TIME = 350       #ha időre fut a kód, akkor a start signal után az input() helyére sleep(...)
RESIST_TIME = 10
EPOCH_LEN = 30         #30 s-nyi epochokkal dolgozik
YASA_INPUT_LEN = 2*60        #percben (az epoch 30 s)

#EEG metadata values

NAME = "PG"
MALE = True
AGE = 22

#file managing

FILE_IDENTIFIER = "full_night_audio"
FILE_FOLDER_NAME = "C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files"

#audiofeedback

DELAY = 10    #hány epochal a kezdés után indul el a mérés
CHECK_LEN = 8

#EZT A NÉGYET KELL ÁLLÍTANI, MÁSHOZ NE NYÚLJATOK
FREQUENCY_RIGHT = 250
FREQUENCY_LEFT = 253
N2_N3 = 1
N3 = 0.5

#sleepstaging first wake hour file path

ONE_HOUR_WAKE = r"C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\one_hour_wake.pkl"

