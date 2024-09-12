import yasa
import matplotlib.pyplot as plt
import pandas as pd


# Bemeneti szöveg feldolgozása
def feldolgozas(szoveg):
    alvasi_fazisok = []
    fazis_lista = ["R", "N1", "N2", "N3", "W"]

    # Sorokat feldaraboljuk
    sorok = szoveg.splitlines()
    print(f"A beolvasott sorok száma: {len(sorok)}")  # Ellenőrzés: hány sort olvasott be

    for sor in sorok:
        tiszta_sor = sor.strip()  # Sor tisztítása
        print(f"Tiszta sor: '{tiszta_sor}'")  # Ellenőrzés: a tisztított sor megjelenítése

        if tiszta_sor in fazis_lista:
            print(f"Alvási fázis talált: {tiszta_sor}")  # Ellenőrzés: melyik fázis talált
            alvasi_fazisok.append(tiszta_sor)

    print(f"Az összes feldolgozott alvási fázis: {alvasi_fazisok}")  # Ellenőrzés: a végső lista
    return alvasi_fazisok




def create_hypnogram_from_list(stage_list):

    if not stage_list:
        print("Az alvási fázisok lista üres.")
        return

    plt.figure(figsize=(int(len(stage_list) / 40), 5))

    try:
        # Hipnogram készítése és megjelenítése
        hypn = yasa.Hypnogram(stage_list, freq="30s")
        hypn.plot_hypnogram(lw=2, fill_color="whitesmoke")
        plt.show()
    except Exception as e:
        print(f"Hiba történt a hipnogram készítése során: {e}")
    finally:
        plt.close()



def create_sleep_statistics_from_list(stage_list):


    # Alvási fázisok átalakítása integer formátumra
    stages_int = yasa.hypno_str_to_int(stage_list)

    # Alvási statisztikák kiszámítása
    statistics = yasa.sleep_statistics(stages_int, sf_hyp=1 / 30)

    # Statisztikai adatok táblázatként való megjelenítése
    stat_df = pd.DataFrame(list(statistics.items()), columns=['Parameter', 'Value'])

    plt.figure(figsize=(4, 6))
    plt.title('Sleep Statistics')
    plt.axis('off')

    # Táblázat létrehozása
    plt.table(cellText=stat_df.values, colLabels=stat_df.columns, loc='center', cellLoc='center',
              colColours=['lightgray'] * 2)

    plt.tight_layout()
    plt.show()
    plt.close()

# Fő program
fajl_nev = "C://Users//pinde//Desktop//09.12_hibas.txt"

# Fájl beolvasása
try:
    with open(fajl_nev, "r", encoding="utf-8") as fajl:
        szoveg = fajl.read()
except FileNotFoundError:
    print(f"A fájl nem található: {fajl_nev}")
    szoveg = ""

# Alvási fázisok kigyűjtése és mentése
alvasi_fazisok = feldolgozas(szoveg)
print(f"Az alvási fázisok listája: {alvasi_fazisok}")

create_sleep_statistics_from_list(alvasi_fazisok)
create_hypnogram_from_list(alvasi_fazisok)


