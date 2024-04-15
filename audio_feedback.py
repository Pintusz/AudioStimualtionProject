import numpy as np
import sounddevice as sd
import time
import threading
import constants as c


# Globális változók
sample_rate = 44100
phase_left = 0
phase_right = 0
is_playing = False
last_call_time = 0
controller_lock = threading.Lock()
stream = None
volume = 0.2
max_volume = 1
past_first_N3 = False


def check_pip(tester_list):
    """
    Ellenőrzi,
    hogy szükséges e az adott epochra az audiofeedback

    - Itt implementáljuk a logikát, ami dönt a feedbackról. Ez visszamenőleg tudja elemezni a listát
      és ennek megfelelően dönt
    - Meghívhatja az audio_controller és az analyze_file is
    - Addig nincsen feedback, amég az első N3 ciklus meg nem történt, hogy az alvás megszilárduljon. 

    :param tester_list: Yasa_output_list, vagy kimentett lista
    :return: bool, szükséges e az audiofeedback az aktuális epochra
    """
    global past_first_N3
    if not past_first_N3:
        last_ten = [{k: v for k, v in elem.items() if k != 'Stage'} for elem in tester_list[-10:]]
        deep_sleep_met = all((elem['N3'] > 0.6) for elem in last_ten)
        if deep_sleep_met:
            past_first_N3 = True
    else:
        last_probas = [{k: v for k, v in elem.items() if k != 'Stage'} for elem in tester_list[-c.CHECK_LEN:]]
        all_conditions_met = all((elem['N2'] + elem['N3'] > c.N2_N3) and (elem['N3'] <= c.N3) for elem in last_probas)
        return all_conditions_met


def callback(outdata, frames, time, status):
    """
    Létrehozza
    a binaurális ütemet

    - Létrehozza és betölti folyamatosan a binautális ütemet a streameléshez, és követi a fázist
    - Korrigálja a túlcsordulást a végén
    """
    global phase_left, phase_right, volume
    t = (np.arange(frames) / sample_rate).reshape(-1, 1)
    left = np.sin(2 * np.pi * c.FREQUENCY_LEFT * t + phase_left) * volume
    right = np.sin(2 * np.pi * c.FREQUENCY_RIGHT * t + phase_right) * volume
    outdata[:] = np.hstack([left, right])
    phase_left += 2 * np.pi * c.FREQUENCY_LEFT * frames / sample_rate
    phase_right += 2 * np.pi * c.FREQUENCY_RIGHT * frames / sample_rate
    phase_left = phase_left % (2 * np.pi)
    phase_right = phase_right % (2 * np.pi)


def start_stream():
    """
    Ha nem megy,
    elindítja a lejátszást

    - Létrehozza a streamet, és a callbackból betöltött adatok alapján lejátsza.
    - A sample_rate az az általános, a blocksize az, hogy mennyi adatot tölt előre be a függvény.
    - Nekem nem kell hogy dinamikus legyen, viszont így egy másodpercnyit előre betölt ami így robusztus
      lesz kellően, és nem recseg amikor nagyobb számításigény merül fel a kódban

    """
    global is_playing, stream, volume
    if not is_playing:
        volume = 0.2
        stream = sd.OutputStream(channels=2, callback=callback, samplerate=sample_rate, blocksize=sample_rate)
        stream.start()
        is_playing = True


def stop_stream():
    """
    Leállítja a lejátszást és beállítja a flaget
    """
    global is_playing, stream
    if is_playing:
        stream.stop()
        is_playing = False


def audio_controller(yasa_output_list):
    """
    Irányítja
    a lejátszást

    - Ezt hívja meg közvetlenül minden kiszámolt epoch-kal a yasa_sleep_classifier.
    - Átadja a yasa_output_listet a check_pip-nek ami ez alapján eldönti hogy kell e lejátszás, és visszatér egy
      bool értékkel.
    - Ez alapján meghívja a start és stop_streamet. Ha nincs változás Akkor nem nyúl bel, hogy folytonos legyen a
      lejátszás
    - Ha valami miatt egy percig nincs hívás leállítja a lejátszást
    """
    global is_playing, last_call_time, controller_lock, volume
    should_play = check_pip(yasa_output_list)
    with controller_lock:
        current_time = time.time()

        if is_playing and (current_time - last_call_time >= 60):
            stop_stream()
            print("Az idő hossza miatt állt le")
            return
        if should_play and not is_playing:
            start_stream()
        elif not should_play and is_playing:
            stop_stream()
        elif should_play and is_playing:
            volume = min(volume + 0.2, max_volume)

        last_call_time = current_time


