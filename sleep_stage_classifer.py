"""
A beérkező adatokat epochokra bontja, és alkalmazza a 'yasa' alvási fázis
osztályozó metódust

- A 'YASA' egy open-source előtanított osztályozó metóus: https://raphaelvallat.com/yasa/build/html/index.html
- Egy epoch-lista folyamatosan töltődik (30s-nyi adat a frek függvényében)
- Egy lista, ami alapján a 'yasa' klasszifikál majd folyamatosan töltődik ebből, nagysága állítható, optimalizálandó
- Ezt a bemeneti listát raw EDF változóvá alakítjuk a szabványok szerint, mert ezt tudja kezelni a 'yasa'

  Megtörténik a klasszifikáció, ennek három kimenete van:
    - Printeli a prediktált értéket (betűjelek) amikor elkészül, tehát kb. 3    0 s-onkékt.
    - Feltölt egy globális listát, amiből majd a fájl megíródik.
    - Az aktuális érték továbbadódik az audio_feedbacknak, ami döntést hoz ez alapján a hangstimulációról


"""

import yasa
import mne
import numpy as np
import pickle
import constants as c
import audio_feedback as a

epoch_data_list = []  # egy epochnyi adat
yasa_output_list = []  # a fájlba írandó lista folyamatos bővüléggel
one_hour_list = []


with open(c.ONE_HOUR_WAKE, 'rb') as file:
    yasa_input_list = pickle.load(file)
    print("egy óra beolvasva")

def yasa_classifier(raw):
    """
    A beérkező nyers EEG adatokból meghatározza epochonként az
    alvási fázist és a valószínűségeket

    - A yasa.SleepStaging parancs tölti be az EDF adatokat a sls ('yasa'-ba töltött (változtatható nagyságú)
      adathalmazt tartalmazó saját típusú) változóba. A 'yasa' kizárólag EGY! elektródával működik,
      ezért célszerű egy central-derivationt megadni (változtatható). Az alany metaadatai a constants-ban
      változtathatóak. Ez után a

        - .predict() fél perces epochok készítése után a fázisoknak megfelelő betűjelek listájával tér vissza.
        - .predict_proba() az ugyanezen 5 s-es epochoknál az egyes alvási fázisokhoz tartozó valószínűségekkel
          (5 fázis: N1, N2, N3, R, W) tér vissza.
    - A raw, amit meghívással kap mindig egy óra hosszúságú adat, az alvás elején az ébrenlét előre felvett adataival
      kiegészítve. Minél hosszabb időtartam adott a yasa-nak, annál pontosabb, egy óránál többet nem akartam, ez
      stabilabb futásidőt eredményez mint pl 8 óra, és állandó, ezzel sokkal pontosabb, mintha 5 percet adnánk neki
      az elején, és később is, vagy később többet, így állandó szinten van a minőség az egész mérés alatt
    - A végén kiíratja az aktuális 30 s állapotát, és meghívja az audio_feedback-ból az audio_controllert, ami elvégzi
      az audiostimulációt ha szükséges.
    :param raw: EDF fájl
    """
    global yasa_output_list, first_call
    sls = yasa.SleepStaging(raw, eeg_name="O1-O2", metadata=dict(age=c.AGE, male=c.MALE))
    y_pred = sls.predict()
    y_proba = sls.predict_proba()

    y_pred_last = y_pred[-1]
    y_proba_last = y_proba.iloc[-1].to_dict()
    yasa_output_list.append({"Stage": y_pred_last, **y_proba_last})
    a.audio_controller(yasa_output_list)
    print(y_pred_last)


def raw_object_maker(yasa_input_list):
    """
    A beérkező adatokból a 'yasa' számára feldolgozható
    EDF fájlt készít

    - Az eszközből a yasa_input_list-be töltött adatok párosával (2 elemű listaként) érkeznek. Ezt először kezelni kell.
    - Létrehozzuk az egyes elektródák értékeit tároló változókat, és ebbe töltjük az összes értéket,
      így a dupla elemek megszűnnek
    - Elvégezzük az EDF formátum megvalósításához szükséges formázásokat
    - Elkészítünk central-derivationokat, később ezeket az EEG csatornákat lehet a 'yasa' klasszifikálónak beadni,
      a kapott és kiszámolt EEG adatok listáival, az EEG nevekkel és a mintavételi
      frekvenciával létrehozzuk az EDF fájlt.
    - Meghívjuk a yasa_classifier függvényt
    :param yasa_input_list: Az apoch_maker által meghatározott méretűbrainBitből érkező lista (dupla elemekkel)
    """
    o1_data = []
    o2_data = []
    t3_data = []
    t4_data = []

    for obj in yasa_input_list:
        o1_data.append(obj.O1)
        o2_data.append(obj.O2)
        t3_data.append(obj.T3)
        t4_data.append(obj.T4)

    o1_np = np.array(o1_data)
    o2_np = np.array(o2_data)
    t3_np = np.array(t3_data)
    t4_np = np.array(t4_data)

    o1_o2_derivation = o2_np - o1_np
    t3_t4_derivation = t4_np - t3_np

    eeg_data = np.array([o1_np, o2_np, t3_np, t4_np, o1_o2_derivation, t3_t4_derivation])

    ch_names = ['O1', 'O2', 'T3', 'T4', 'O1-O2', 'T3-T4']
    ch_types = ['eeg'] * 6
    info = mne.create_info(ch_names=ch_names, sfreq=c.SAMPLING_FREQ, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    yasa_classifier(raw)


def epoch_maker(data):
    """
    A beérkező nyers adatból elkészíti a szükséges méretű listát, amelyet továbbít közvetetten a
    klasszifikálónak

    A listák méretei itt változtathatóak meg!

    - A BrainBit-ből érkező jelekkel feltöltjük az epoch_data_listet. Mivel minden meghíváskor új adat érkezi
      ezért globális változó, hogy ne inicializálódjon újra
    - A constonts.py-ban megadható a sampling freq és az apoch mérete, de ezek maradjanak változatlaul
    - Ha az epoch_data_list megtelik adattal hozzáadódik egy nagy listához és kiürül, újratöltődik
    - A yasa_input listet inicializáláskor feltöltjük egy órányi nyers ébrenléti adattal. Ehhez hozzáadódnak az új
      epochot, és folyamatosan tölrlődnek az elsők, így ablakolunk, mindig egy órányi adattal hívjuk meg a
      raw_object_makert
    - Ez a yasa miatt lesz fontos


    :param data: BrainBit-ből érkező nyers adat
    """
    global epoch_data_list, yasa_input_list
    epoch_data_list_len = int(c.SAMPLING_FREQ * c.EPOCH_LEN)

    for elem in data:
        epoch_data_list.append(elem)

    if len(epoch_data_list) >= epoch_data_list_len:
        yasa_input_list.extend(epoch_data_list)
        epoch_data_list = []

        if len(yasa_input_list) > (c.YASA_INPUT_LEN * epoch_data_list_len):
            del yasa_input_list[:epoch_data_list_len]

        raw_object_maker(yasa_input_list)


"""
#Ezzel vettem fel az egy óra ébrenlétet, ha még szükség lesz rá. 
def save_data_with_pickle(data_list): #csak az egy órás adathoz kellett
    f_path = r"C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\one_hour_wake.pkl"
    with open(f_path, 'wb') as file:
        pickle.dump(data_list, file)

def process_data(data):   #csak az egy órás adathoz kellett

    global one_hour_list
    for elem in data:
        one_hour_list.append(elem)

    if len(one_hour_list) >= c.EPOCH_LEN * c.SAMPLING_FREQ * 2 * 60: #ezt 60 ra lesz egy óra
        save_data_with_pickle(one_hour_list)
        one_hour_list.clear()
"""
