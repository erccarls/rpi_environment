import Adafruit_DHT
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from w1thermsensor import W1ThermSensor


EXECUTOR = ThreadPoolExecutor(16)
SENSOR_MAP = {
    'DHT11': Adafruit_DHT.DHT11,
    'DHT22': Adafruit_DHT.DHT11,
    'DS18B20': 'DS18B20'
}


def read_humidity_and_temp(sensor_spec):
    """
    Read an individual DHT11, DHT22, or DS18B20 sensor. If DS18B20 is passed for
    the sensor key, pin is ignored as it is assumed to be on the active single
    wire interface.

    Parameters
    ----------
    sensor_spec

    Returns
    -------
    humidity: float or NoneType
    temperature: float, list(float) or NoneType
        Temp or list of temps in the case of DS18B20 units in degrees celsius.
    """
    sensor = SENSOR_MAP[sensor_spec['sensor']]
    pin = sensor_spec['pin']

    if sensor in {Adafruit_DHT.DHT11, Adafruit_DHT.DHT22}:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries=5)
        return humidity, temperature
    elif sensor == 'DS18B20':
        temperatures = W1ThermSensor().get_temperatures(
            units=[W1ThermSensor.DEGREES_C for _ in W1ThermSensor.get_available_sensors()])
        return None, temperatures
    else:
        raise ValueError('Sensor type %s not supported' % sensor)


def get_average_humidity_and_temp(sensors=[dict(sensor='DHT11', pin=26)]):
    """
    Obtain the average temperature and humidity readings from a list of DHT11/22
    or DS18B20 sensors. If humidity is unavailable or iof temp and humidity are
    None for some sensors, that reading is ignored. Sensor reads are done
    concurrently via a ThreadPoolExecutor. If not sensors can be read, a
    LookupError is raised.

    Parameters
    ----------
    sensors: list(dict)
        List of dictionaries containing 'sensor' and 'pin'. The pin is the GPIO
        pin (BCM). Sensor can take on the following values.
            'DHT11' = Adafruit_DHT.DHT11
            'DHT22' = Adafruit_DHT.DHT11
            'DS18B20' = 'DS18B20'

    Returns
    -------
    stats: dict()
        Dictionary with summary statistics around temperature and humidity.
    """
    temps, humidities = [], []

    futures = EXECUTOR.map(read_humidity_and_temp, sensors)

    for future in futures:
        humidity, temperature = future
        if temperature is not None:
            if isinstance(temperature, float):
                temps.append(temperature)
            else:
                temps += temperature
        if humidity is not None:
            humidities.append(humidity)

    if not temps or not humidities:
        raise LookupError('No valid readings found for one or both of temperature'
                          ' and humidities. Check pinouts and sensor specifications.')

    return {
        'humidity_avg': np.average(humidities),
        'humidity_std': np.std(humidities),
        'humidity_n_sensors': len(humidities),
        'temperature_avg': np.average(temps),
        'temperature_std': np.std(temps),
        'temperature_n_sensors': len(temps)
    }


if __name__ == '__main__':
    print(get_average_humidity_and_temp())



