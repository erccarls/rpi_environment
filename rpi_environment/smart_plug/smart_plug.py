from pyHS100 import Discover, SmartPlug


def device_from_name(name):

    devices = list(Discover.discover().values())

    names = [dev.alias for dev in devices]
    try:
        return devices[names.index(name)]
    except ValueError as e:
        print('Could not find device "%s" in devices %s' % (name, names))
        raise e
