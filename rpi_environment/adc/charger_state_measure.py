import time
import busio
import digitalio
import board
import threading
import signal
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


class ChargerStateReader:

    def __init__(self,
                 n_channels=1,
                 ref_voltage=3.3,
                 threshold=.6,
                 charger_off_callback=None,
                 charger_on_callback=None):

        self.n_channels = n_channels
        self.ref_voltage = ref_voltage
        self.threshold = threshold
        self.charger_off_callback = charger_off_callback
        self.charger_on_callback = charger_on_callback

        # Init serial port
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

        # This pin doesn't seem to matter?!?
        self.cs = digitalio.DigitalInOut(board.D24)
        self.mcp = MCP.MCP3008(self.spi, self.cs, self.ref_voltage)
        self.channels = [AnalogIn(self.mcp, getattr(MCP, 'P{}'.format(i))) for i
                         in range(self.n_channels)]

        # Init Thread
        self._read_thread = threading.Thread(target=self._read_charger_loop)
        self._read_thread_isalive = False
        self._charger_states = None

    def _read_charger_loop(self):
        while self._read_thread_isalive:
            new_states = ['off' if v < self.threshold else 'on' for v in
                          self.get_voltages()]
            # First iteration needs to be set.
            if self._charger_states is None:
                self._charger_states = new_states

            turned_on = []
            turned_off = []

            for channel, (prev_state, new_state) in enumerate(
                    zip(self._charger_states, new_states)):
                if prev_state == 'off' and new_state == 'on':
                    turned_on.append(channel)
                elif prev_state == 'on' and new_state == 'off':
                    turned_off.append(channel)

            if turned_on != [] and self.charger_on_callback is not None:
                self.charger_on_callback(turned_on)

            if turned_off != [] and self.charger_off_callback is not None:
                self.charger_off_callback(turned_off)

            self._charger_states = new_states
            time.sleep(1)

    def start(self):
        self._read_thread_isalive = True
        self._read_thread.start()

        while self._charger_states is None:
            time.sleep(.01)

    def shutdown(self):
        print('Shutting Down Reader Thread')
        self._read_thread_isalive = False
        self._read_thread.join()

    def get_voltages(self):
        return [channel.voltage for channel in self.channels]

    def get_raw_values(self):
        return [channel.value for channel in self.channels]

    def get_charger_states(self):
        if self._charger_states is None:
            raise RuntimeError('State cannot be read until start() is called.')
        return self._charger_states


def charger_on_callback(charger_state_changes):
    print('Chargers are ON :)', charger_state_changes)


def charger_off_callback(charger_state_changes):
    print('Chargers are OFF :(', charger_state_changes)


def signal_handler(sig, frame):
    csr.shutdown()


if __name__ == '__main__':
    csr = ChargerStateReader(n_channels=1,
                             charger_on_callback=charger_on_callback,
                             charger_off_callback=charger_off_callback)

    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)

    csr.start()
