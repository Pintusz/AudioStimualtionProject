"""
BrainBit eszköz kezelése, adatok fogadása,
kommunikáció az eszközzel.

Ezt futtatni!

Az on_signal_recieved-ből lehet kinyerni a beérkező adatot. Specifikációja a leírásában.
"""
from neurosdk.scanner import Scanner
from neurosdk.cmn_types import *
import concurrent.futures
from time import sleep
import constants as c
import sleep_stage_classifer as s
import audio_feedback as a
import file_manager as f

def sensor_found(scanner, sensors):
    """
    Kiíratja az összes hatókörön belüli szenzort
    """
    for index in range(len(sensors)):
        print('Sensor found: %s' % sensors[index])

def on_sensor_state_changed(sensor, state):
    """
    Ha a szenzor állapota megváltozik (pl.: disconnect) kiírja
    """
    print('Sensor {0} is {1}'.format(sensor.name, state))

def on_battery_changed(sensor, battery):
    """
    Amikor a szenzor töltöttségi állapota megváltozik kiírja az értékét
    """
    print('Battery: {0}'.format(battery))

def on_signal_received(sensor, data):
    """
    Ha beérkezik jel a szenzorból, továbbadja
    és elindítja a feldolgozást.\n
    A sleep_stage_classifiernek adjuk itt át a 'data' beérkező adatot.\n
    Fontos! az adatok páronként érkeznek, de minden elem megfelel egy mérésnek.
    A PackNum, ami meghatározza melyik adat érkezett, kettőnél megegyezik (250 Hz-en biztosan),
    egy lista két eleme, ilyen listákból áll a 'data'. Pl.: 2 s alatt 250 Hz-en 250 PackNum-nyi adat érkezik,
    de ez 500 mintát jelent, a frekvencia rendben van tehát. Ezeket később választjuk szét.
    """
    s.epoch_maker(data)

def on_resist_received(sensor, data):
    """
    Ha ellenállást mérünk, amikor új adat érkezikkiírja Ohm-ban az egyes elektródák értékeit.
    """
    print(data)

try:
    """
    Irányítja a kezelést
    
    - Inicializálja a szenzort, és 5 s-ig keresi a hatókörben. A scanner csak eddig fut. (Elég)
    - Kiír minden információt, és létrehoz egy sensor-t, inicializálja a fenti függvényeket.
    - Kiírja az alap adatokat, a sorozatszámot és frekvenciát a biztonság kedvéért
    - Futtat egy constants-ban meghatározott idejű ellenállásmérést, kiírja (Vált. lehet)
    - Futtatja az adatgyűjtést addig, amég input nem jön(felébredtünk) (enter), akkor leállítja
    - Ekkor futtatja a fájlbamentést, ami egy globális változóból ment, csv fájlba. (file_manager)
    - Ezt a globális listát biztonsági okokból töröljük
    - Lecsatlakozik és eltávolítja a szenzort
    """
    scanner = Scanner([SensorFamily.LEBrainBit, SensorFamily.LEBrainBitBlack])

    scanner.sensorsChanged = sensor_found
    scanner.start()
    print("Starting search for 5 sec...")
    sleep(5)
    scanner.stop()

    sensorsInfo = scanner.sensors()
    for i in range(len(sensorsInfo)):
        current_sensor_info = sensorsInfo[i]
        print(sensorsInfo[i])


        def device_connection(sensor_info):
            return scanner.create_sensor(sensor_info)


        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(device_connection, current_sensor_info)
            sensor = future.result()
            print("Device connected")

        sensor.sensorStateChanged = on_sensor_state_changed
        sensor.batteryChanged = on_battery_changed

        sensFamily = sensor.sens_family

        sensorState = sensor.state
        if sensorState == SensorState.StateInRange:
            print("connected")
        else:
            print("Disconnected")

        print("sensor serial number:", sensor.serial_number) #az eszköz beazonosítása

        if sensor.is_supported_parameter(SensorParameter.SamplingFrequency):
            if sensor.sampling_frequency == sensor.sampling_frequency.FrequencyHz250:
                print("sampling frequency:", 250, "Hz")
            else:
                print("sampling frequency changed:", sensor.sampling_frequency)

        if sensor.is_supported_feature(SensorFeature.Resist):
            sensor.resistDataReceived = on_resist_received

        if sensor.is_supported_feature(SensorFeature.Signal):
            sensor.signalDataReceived = on_signal_received

        if sensor.is_supported_command(SensorCommand.StartResist):
            sensor.exec_command(SensorCommand.StartResist)
            print("Start resist")
            sleep(c.RESIST_TIME)
            sensor.exec_command(SensorCommand.StopResist)
            print("Stop resist")

        if sensor.is_supported_command(SensorCommand.StartSignal):
            sensor.exec_command(SensorCommand.StartSignal)
            print("Start signal")
            input()
            sensor.exec_command(SensorCommand.StopSignal)
            print("Stop signal")
            a.stop_stream()
            f.sleep_stage_file_maker()      #stop signal után menti el fájlba az eredményt
            s.yasa_output_list.clear()      #biztonság kedvéért törli a nagy listákat
            s.yasa_input_list.clear()

        sensor.disconnect()
        print("Disconnect from sensor")
        del sensor

    del scanner
    print('Remove scanner')
except Exception as err:
    print(err)
