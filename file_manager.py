"""
Az egész mérés adataiból csv fájl írása, a fájlok vizualizálása,
feldolgozása

Feldolgozáshoz beírni az analyze_file()-ba a fájl abszolút elérési útvonalát és ezt futtatni.
"""

import os
import datetime
import pandas as pd
import constants as c
import sleep_stage_classifer as s
import visualizer as v


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
    v.analyze_file(file_path)



