"""
Az egész mérés adataiból csv fájl írása, a fájlok vizualizálása,
feldolgozása

Feldolgozáshoz beírni az analyze_file()-ba a fájl abszolút elérési útvonalát és ezt futtatni.
"""

import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import yasa
import constants as c
import sleep_stage_classifer as s
import audio_feedback as a


def sleep_stage_file_maker():
    """
    Létrehoz egy csv. fájlt az mérés során felvett összes
    adatból

    A névkonvenció: hóvap_nap_file_identifier. Az atuális hónap nap, a file_identifiert pedig a
    constants-ban lehet beállítani. (pl.:full_night, vagy test)

    A mentés helye az output_files (C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files)
    DataFrame-ből csv írása, mentődnek a:
    prediktált alvási fázisok
    és az egyes alvási fázisok valószínűségei minden 30s epochra.
    Pl egy sor: W, 0.22, 0.4, 0.28, 0.01, 0.99 (5 fázis: N1, N2, N3, R, W)

    """
    current_date = datetime.datetime.now().strftime("%m_%d")
    file_name = f"{current_date}_{c.FILE_IDENTIFIER}.csv"  # A fájl neve most tartalmazza a dátumot
    file_path = os.path.join(c.FILE_FOLDER_NAME, file_name)  # Célmappa megadása

    yasa_output_df = pd.DataFrame(s.yasa_output_list)
    yasa_output_df.to_csv(file_path, index=False)


def analyze_file(csv_file_path):
    """
    Fájl feldolgozása, statisztika, valószínűségi plot,
    hisztogram.

    - A csv.-t feldolgozzuk, külön DataFrame-be kerülnek a betűvel jelzett 'Stage'-k és az 5 oszlopnyi 'Probability'.
    - Ábrázoljuk egy 'yasa' parancssor alapján a hisztogramot. Méretét az adatok mennyisége határozza meg.
    - Ábrázoljuk 'matplotlib'-bel a valószínűségeket (ahogy a 'yasa'-ban is, de az fájlból nem működik). Méretét az
      adatmennyiség határozza meg.
    - Ábrázoljuk az összes szükséges értéket és kimutatást 'yasa' függvény segítségével.
    - A c.SHOW_FEEDBACK egy kapcsoló, jelzi (kiemelővel a valószínűségploton) hogy mikor volt a check_pip szerint audio
      stimuláció. Mindig az aktuális check_pip feltételekre!
    :param csv_file_path: output_list-be mentett .csv fájlok abszolút elérési útvonala
    """
    df = pd.read_csv(csv_file_path)
    stages = df['Stage']
    probabilities = df.iloc[:, 1:]  # Az első oszlop a 'Stages', a többi a valószínűsége
    stages_int = yasa.hypno_str_to_int(stages)

    if c.SHOW_FEEDBACK:
        dict_list = df.to_dict(orient='records')
        pip_results = [a.check_pip(dict_list[:i + 1]) for i in range(len(dict_list))]

    # Hipnogram ábrázolása
    plt.figure(figsize=(int(len(stages) / 40), 5))
    hypn = yasa.Hypnogram(stages, freq="30s")
    hypn.plot_hypnogram(lw=2, fill_color="whitesmoke")
    plt.show()

    # Valószínűségplot ábrázolása
    colors = ["#99d7f1", "#009DDC", "xkcd:twilight blue", "xkcd:rich purple", "xkcd:sunflower"]
    ax = probabilities.plot(kind='area', figsize=(int(len(probabilities) / 6), 5), stacked=True, color=colors,
                            alpha=0.8, linewidth=0)
    ax.set_xlabel('Time (30-sec epoch)')
    ax.set_ylabel('Probability')
    ax.legend(frameon=False, bbox_to_anchor=(1, 1))

    if c.SHOW_FEEDBACK:
        for i, result in enumerate(pip_results):
            if result:  # Ha True, akkor kiemeljük az adott szakaszt
                ax.axvspan(i, i + 1, color='yellow', alpha=0.5)  # Kiemelés sárga színnel
        plt.show()
    #    print((sum(pip_results) / 2), "percnyi ingerlés volt összesen")

    # Alvási statisztikák kiíratása táblázatban
    statistics = yasa.sleep_statistics(stages_int, sf_hyp=1 / 30)
    stat_df = pd.DataFrame(list(statistics.items()), columns=['Parameter', 'Value'])
    plt.figure(figsize=(4, 6))
    plt.title('Sleep Statistics')
    plt.axis('off')
    plt.table(cellText=stat_df.values, colLabels=stat_df.columns, loc='center', cellLoc='center',
              colColours=['lightgray'] * 2)
    plt.tight_layout()
    plt.show()


if c.ANALYZE_FILE:
    analyze_file(
        r'C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files\02_28_full_night_audio2.csv')
