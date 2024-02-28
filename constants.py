#data/device managing

SAMPLING_FREQ = 250     #mintavételi freq, ez stabil, írja, ha megváltozik, nem változtatni
SIGNAL_TIME = 350       #ha időre fut a kód, akkor a start signal után az input() helyére sleep(...)
RESIST_TIME = 5
EPOCH_LEN = 30         #30 s-nyi epochokkal dolgozik
YASA_INPUT_LEN = 2*60        #percben (az epoch 30 s)

#EEG metadata values

MALE = True
AGE = 22

#file managing

FILE_IDENTIFIER = "full_night_audio2"
FILE_FOLDER_NAME = "C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files"
ANALYZE_FILE = True     #ábrázoljuk a mentett fájlokat. Futtatásnál false
SHOW_FEEDBACK = True    #sárgával színezi, hogy a check_pip alapján mikor volt ing. Aktuális check_pip!

#audiofeedback

CHECK_LEN = 3
FREQUENCY_RIGHT = 138   #a kettő különbségét érzékeljük a sztereo hangzásból
FREQUENCY_LEFT = 135

#sleepstaging first wake hour file path

ONE_HOUR_WAKE = r"C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\one_hour_wake.pkl"

