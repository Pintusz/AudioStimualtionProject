import pandas as pd
import matplotlib.pyplot as plt
import yasa
import os
import audio_feedback as a
import constants as c
from datetime import datetime, timedelta
import sleep_stage_classifer as s


def txt_maker(file_path):
    """
    Szöveges
    fájlba kimenti az ingerlési és egyéb adatokat.

    Params:
        file_path (str): A szöveges fájl elérési útvonala és neve, ahová a szöveg mentésre kerül.
    """


    finish_time = datetime.now()
    start_time = finish_time - timedelta(seconds=len(s.yasa_output_list) * c.EPOCH_LEN)

    generated_text = f"Kezdés ideje: {start_time.strftime('%Y-%m-%d %H:%M')}\n"
    generated_text += f"Befejezés ideje: {finish_time.strftime('%Y-%m-%d %H:%M')}\n"
    generated_text += f"Ingerlés: \n Az első teljes N3 ciklusig nincs ingerlés\n"
    generated_text += f"Az utolsó {c.CHECK_LEN} epochban ellenőrzi a feltételek teljesülését.\n"
    generated_text += f"Audio_feedback történik az éjszaka folyamán\n"
    generated_text += f"Leáll, ha az N3 valószínűsége átlépi a {c.N3} értéket, vagy W valószínűsége átlépi a {c.W} értéket\n"
    generated_text += f"Az alvás eslő {c.TERMINATE/120} órájában van ingerlés"
    generated_text += f"A binaurális ütem jobb oldali vivőfrekvenciája {c.FREQUENCY_RIGHT}, a bal {c.FREQUENCY_LEFT} Hz\n"
    generated_text += f"Az ütem frekvenciája: {c.FREQUENCY_RIGHT-c.FREQUENCY_LEFT}"

    with open(file_path, "w") as text_file:
        text_file.write(generated_text)


def analyze_file(csv_file_path):

    """
    Vizualizálja,
    és menti az alvás eredményeit

    - Feldolgozza a mérés végén létrejött csv fájlt.
    - Hypnogramot, valószínűség-plotot ábrázol az alvási fázisokról az idő függvényében, és alvási statisztikát készít.
    - A valószínűség-ploton ábrázolja az aktuális audiofeedback logika szerint, hogy mikor volt az alvás alatt visszajelzés
    - A plotokat kimenti a meghatározott helyre
    - Ment egy Adatok.txt fájlt, ami a mérés beállításait tartalmazza röviden
    - A kikommentelt részbe a kívánt elérési útvonalat beírva és futtatva tetszőleges fájlt lehet elemezni, DE figyelni a logika megváltozására

    """
    a.past_first_N3 = False #a mentéshez az első N3-at ne számolja bele
    base_dir = "C:\\Users\\pinde\\OneDrive\\Szakdolgozat\\Mérések"
    today = datetime.now().strftime("%m.%d")  # MM.DD formátum
    save_dir = os.path.join(base_dir, today)
    counter = 1

    original_save_dir = save_dir
    while os.path.exists(save_dir):
        save_dir = f"{original_save_dir}_{counter}"
        counter += 1

    os.makedirs(save_dir)

    df = pd.read_csv(csv_file_path)
    stages = df['Stage']
    probabilities = df.iloc[:, 1:]  # Az első oszlop a 'Stages', a többi a valószínűsége
    stages_int = yasa.hypno_str_to_int(stages)

    dict_list = df.to_dict(orient='records')
    pip_results = [a.check_pip(dict_list[:i + 1]) for i in range(len(dict_list))]

    # Hipnogram ábrázolása, megjelenítése és mentése
    plt.figure(figsize=(int(len(stages) / 40), 5))
    hypn = yasa.Hypnogram(stages, freq="30s")
    hypn.plot_hypnogram(lw=2, fill_color="whitesmoke")
    hypno_save_path = os.path.join(save_dir, "hypnogram.png")
    plt.savefig(hypno_save_path)
    plt.show()
    plt.close()

    # Valószínűségplot ábrázolása, megjelenítése és mentése
    colors = ["#99d7f1", "#009DDC", "xkcd:twilight blue", "xkcd:rich purple", "xkcd:sunflower"]
    ax = probabilities.plot(kind='area', figsize=(int(len(probabilities) / 6), 5), stacked=True, color=colors,
                            alpha=0.8, linewidth=0)
    ax.set_xlabel('Time (30-sec epoch)')
    ax.set_ylabel('Probability')
    ax.legend(frameon=False, bbox_to_anchor=(1, 1))

    for i, result in enumerate(pip_results):
        if result:  # Ha True, akkor kiemeljük az adott szakaszt
            ax.axvspan(i, i + 1, color='yellow', alpha=0.5)  # Kiemelés sárga színnel

    probability_save_path = os.path.join(save_dir, "probability_plot.png")
    plt.savefig(probability_save_path)
    plt.show()
    plt.close()

    # Alvási statisztikák táblázatának ábrázolása, megjelenítése és mentése
    statistics = yasa.sleep_statistics(stages_int, sf_hyp=1 / 30)
    stat_df = pd.DataFrame(list(statistics.items()), columns=['Parameter', 'Value'])
    plt.figure(figsize=(4, 6))
    plt.title('Sleep Statistics')
    plt.axis('off')
    plt.table(cellText=stat_df.values, colLabels=stat_df.columns, loc='center', cellLoc='center', colColours=['lightgray'] * 2)
    plt.tight_layout()
    statistics_save_path = os.path.join(save_dir, "sleep_statistics.png")
    plt.savefig(statistics_save_path)
    plt.show()
    plt.close()

    text_file_path = os.path.join(save_dir, "Adatok.txt")
    txt_maker(text_file_path)

#analyze_file(r'C:\Programkornyezet\PythonProjects\AudiostimulationProject\AudiostimulationDirectory\output_files\04_15_full_night_audio.csv')
