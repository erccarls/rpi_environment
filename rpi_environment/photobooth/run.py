import sys, os
from concurrent.futures import ThreadPoolExecutor 
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from photobooth import Capture
from rpi_environment.adc.charger_state_reader import ChargerStateReader
from rpi_environment.smart_plug import smart_plug

MODE = "smart_plug" 

if MODE == "photobooth":
    capture = Capture()
    executor = ThreadPoolExecutor()
    executor.submit(capture.main)
    csr = ChargerStateReader(n_channels=2,
                             charger_on_callback=capture.trigger)
    csr.start()
    executor.shutdown(wait=True)
    csr.shutdown()

elif MODE == "smart_plug":
    plug_light = smart_plug.device_from_name("light 1")
    plug_speaker = smart_plug.device_from_name("speaker")
    
    def charger_on_callback(charger_state_changes):
        print('Chargers are ON :)', charger_state_changes)
        print(charger_state_changes)
        if 0 in charger_state_changes:
            plug_light.turn_on()
        if 1 in charger_state_changes:
            plug_speaker.turn_on()

    def charger_off_callback(charger_state_changes):
        print('Chargers are OFF :(', charger_state_changes)
        if 0 in charger_state_changes:
            plug_light.turn_off()
        if 1 in charger_state_changes:
            plug_speaker.turn_off()


    csr = ChargerStateReader(n_channels=2,
                             charger_on_callback=charger_on_callback, 
                             charger_off_callback=charger_off_callback)
    csr.start()

    while True:
        try:
            import time
            time.sleep(1)
        except KeyboardInterrupt:
            csr.shutdown()

            
