import Adafruit_DHT
import numpy as np
from concurrent.futures import ThreadPoolExecutor


EXECUTOR = ThreadPoolExecutor(16)
SENSOR_MAP = {
    'DHT11': Adafruit_DHT.DHT11,
    'DHT22': Adafruit_DHT.DHT11,
    'DS18B20': 'DS18B20'
}


def read_humidity_and_temp(sensor_spec):
    """
    Read an individual DHT11, DHT22, or DS18B20 sensor.

    Parameters
    ----------
    sensor_spec

    Returns
    -------
    humidity, temperature
    """
    sensor = SENSOR_MAP[sensor_spec['sensor']]
    pin = sensor_spec['pin']

    if sensor in {Adafruit_DHT.DHT11, Adafruit_DHT.DHT22}:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries=5)
        return humidity, temperature
    else:
        raise ValueError('Sensor type %s not supported' % sensor)


def get_average_humidity_and_temp(sensors=[dict(sensor=Adafruit_DHT.DHT11, pin=26)]):
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
    avg_humidity: float
        Average humidity reading across all available sensors.
    avg_temperature: float
        Average temperature reading across all available sensors. Units in
        centigrade.
    """
    temps, humidities = [], []

    futures = EXECUTOR.map(read_humidity_and_temp, sensors)

    for future in futures:
        humidity, temperature = future
        if temperature is not None:
            temps.append(temperature)
        if humidity is not None:
            humidities.append(humidity)

    if not temps or not humidities:
        raise LookupError('No valid readings found for one or both of temperature'
                          ' and humidities. Check pinouts and sensor specifications.')

    return np.average(humidities), np.average(temps)


if __name__ == '__main__':
    print(get_average_humidity_and_temp())



