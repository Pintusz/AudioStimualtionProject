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
import time
import constants as c
import audio_feedback as a


epoch_data_list = []  # egy epochnyi adat
yasa_input_list = []  # a yasa-ba bemenő adatmennyiség
yasa_output_list = []  # a fájlba írandó lista folyamatos bővüléggel
first_call = True  # az első 5 perc flagje a yasa_classifier-ben


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
    - A 'yasa' esetéban minél hosszabb időtartamot elemez annál jobb az eredmény, 5 percnél kevesebbet nem tud,
      így az első 5 percet meg kell várni, utána tudjuk epochonként megkapni az értékeket.Ezt kezeli az if/else.
      Az első 5 perc esetén kiírjuk az egész listát, utána, fél percenként ablakolt adatok érkeznek, az ezekből készült
      listából az utolsó elem szükséges/új nekünk. több adat a pontos mérést szolgálja.
    - Az if/else-n belül a prediktálás eredményei, és a valószínűségek, mint dictionary
      a yasa_output_list globális változóhoz adódnak, amiből a file_maker a teljes mérés végén csv. fájlt készít.
    - Kiírja az aktuális értéket
    - Meghívja majd az audio_feedbacket az érték alapján, ami majd meghatározza az audiostimulációt.
    :param raw: EDF fájl
    """
    start_time = time.time()
    global yasa_output_list, first_call
    sls = yasa.SleepStaging(raw, eeg_name="O1-O2", metadata=dict(age=c.AGE, male=c.MALE))
    y_pred = sls.predict()
    y_proba = sls.predict_proba()

    if first_call:
        for i in range(len(y_pred)):
            y_pred_i = y_pred[i]
            y_proba_i = y_proba.iloc[i].to_dict()
            yasa_output_list.append({"Stage": y_pred_i, **y_proba_i})
            print(y_pred_i)
        first_call = False
    else:
        y_pred_last = y_pred[-1]
        y_proba_last = y_proba.iloc[-1].to_dict()
        yasa_output_list.append({"Stage": y_pred_last, **y_proba_last})
        print(y_pred_last)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"Eltelt idő: {elapsed_time} s, y_pred hossza: {len(y_pred)}\n")  # Eltelt idő és az y_pred hosszának kiírása


def raw_object_maker(yasa_input_list):  #névkonvenció? nemtudom
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

    for pair in yasa_input_list:
        for obj in pair:
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
    sfreq = c.SAMPLING_FREQ
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    yasa_classifier(raw)


def epoch_maker(data):
    """
    A beérkező nyers adatból elkészíti a szükséges méretű listát, amelyet továbbít közvetetten a
    klasszifikálónak

    A listák méretei itt változtathatóak meg!

    - A globális változók a többszöri meghívás miatt szerepelnek:
    - Az epoch_data_list egy-egy epoch hosszát határozza meg. Ez ugyan a constants-ban változtatható, de ne változtass,
      a sampling_freq (250 Hz) és az epoch_len (30 s) is adott. /2 a duplikált bemeneti adatok miatt fontos, megoldása
      a raw_object_maker-ben.
    - A beérkező adat hozzáadódik az epoch_data_list-hez. Ez az alapegységünk, 30 s-nyi adat! Ha ez "megtelik"
      hozzáadódik a yasa_input_list-hez, ez az (epoch méret egész többszörösére) változtatható hosszúságú lista,
      amit a 'yasa' klasszifikáló egészben kap meg. Most 15 perc, minél hosszab, annál pontosabb a klasszifikálás,
      de nő a feldolgozási idő is.
    - A YASA_INPUT_LEN a constants-ban változtatható méretű.

      - A yasa-nak szükséges legalább 5 perc, ezért az első 5 percet egyben adjuk át, utána epochonként.
      - Amikor "megtelik" az első epoch törlődik, és egy új hozzáadódik, ablakolunk.


    :param data: BrainBit-ből érkező nyers adat
    """
    global epoch_data_list, yasa_input_list
    epoch_data_list_len = int(c.SAMPLING_FREQ * c.EPOCH_LEN / 2)

    epoch_data_list.append(data)

    if len(epoch_data_list) >= epoch_data_list_len:
        yasa_input_list.extend(epoch_data_list)
        epoch_data_list = []

        if len(yasa_input_list) > (c.YASA_INPUT_LEN) * epoch_data_list_len:
            del yasa_input_list[:epoch_data_list_len]

        if len(yasa_input_list) > epoch_data_list_len * 10:
            raw_object_maker(yasa_input_list)
