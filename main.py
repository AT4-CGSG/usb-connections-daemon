import os
import signal
import sys
from sys import argv

import pyinotify
from pyudev import Device, Context


def print_device(d: Device, action: str = None):
    print_device.__device_properties = [
        ['BUSNUM'],                   # Bus ID
        ['DEVPATH', 'DEVNAME'],       # Device Address
        ['ID_SERIAL', 'ID_MODEL'],    # Product
        ['ID_VENDOR_FROM_DATABASE'],  # Manufacturer
        ['ID_VENDOR_ID'],             # Vendor ID
        ['PRODUCT', 'ID_MODEL_ID'],   # Product ID
    ]

    if d is None \
       or 'DEVNAME' not in d.keys() or 'BUSNUM' not in d.keys() \
       or d['DEVNAME'] is None      or d['BUSNUM'] is None:
        return
    if action is None:
        if d.action != 'add' and d.action != 'remove':  # ignoring -bind actions as it's not stated in the task
            return
        action = 'connected' if d.action == 'add' else 'disconnected'  # store action type in 'action' regardless
    else:
        if action != 'connected' and action != 'disconnected':
            return

    for props in print_device.__device_properties:
        succ = False
        for prop in props:
            prop_data = d.get(prop)
            if prop_data is not None:
                print(prop_data, end=' ')
                succ = True
                break
        if not succ:
            print('N/A', end=' ')
    print(action)


class UsbEventHandler(pyinotify.ProcessEvent):
    __devices = {}
    __context: Context

    def __init__(self, context: Context, **kargs):
        super().__init__(**kargs)
        self.__context = context

    def my_init(self): pass

    """
    ignoring -bind actions as it's not stated in the task        
    """

    def process_IN_ATTRIB(self, event):
        for ddd in self.__context.list_devices(subsystem='usb'):
            if ddd.device_node == event.pathname \
               and ('ID_SERIAL' in ddd.keys() or 'ID_MODEL' in ddd.keys()) \
               and event.pathname not in self.__devices.keys():
                self.__devices[ddd.device_node] = ddd
                print_device(ddd, 'connected')

    # process_IN_CREATE = process_IN_ATTRIB

    def process_IN_DELETE(self, event):
        if event.pathname in self.__devices.keys():
            print_device(self.__devices[event.pathname], 'disconnected')
            self.__devices.pop(event.pathname, None)


def start_monitoring():
    context = Context()

    manager = pyinotify.WatchManager()
    handler = UsbEventHandler(context)
    notifier = pyinotify.Notifier(manager, handler)
    folder = '/dev/bus/usb'
    for sub_fld in os.scandir(folder):
        if sub_fld.is_dir():
            events = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']
            manager.add_watch(folder + '/' + sub_fld.name, events['IN_ATTRIB'] | events['IN_DELETE'], proc_fun=handler)
    notifier.loop()


if __name__ == '__main__':
    original_stdout = sys.stdout

    def safe_stop():
        sys.stdout = original_stdout
        sys.exit(0)

    signal.signal(signal.SIGTERM, lambda signum, frame: safe_stop())

    file_opened = True

    try:
        output_file = open(argv[1], 'w')
    except IndexError:
        file_opened = False
        output_file = sys.stdout  # continue with 'standard' stdout
    except IOError as err:
        file_opened = False
        print('IOError: ', err)
        output_file = sys.stdout  # continue with 'standard' stdout

    sys.stdout = output_file

    try:
        with output_file:  # this will take care about an opened file
            if file_opened:  # no need to erase sys.stdout
                signal.signal(signal.SIGUSR1, lambda signum, frame: output_file.truncate(0))

            start_monitoring()

    except KeyboardInterrupt:
        safe_stop()
    else:
        sys.stdout = original_stdout
