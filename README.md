This program is intended to monitor USB connections. It provides logs about incoming and outcoming connections in following format:

```
Bus ID, Device Address, Product, Manufacturer, Vendor ID, Product ID, Current State
(connected/disconnected)
```

Example:
```
003 /devices/pci0000:00/0000:00:14.0/usb3/3-1 COMPANY_USB_Device A4Tech Co., Ltd. 09da 9da/f613/13a5 disconnected
001 /devices/pci0000:00/0000:00:1a.0/usb1/1-1/1-1.2 COMPANY_USB_Device A4Tech Co., Ltd. 09da 9da/f613/13a5 connected
```

Requirements
-----
[requirements.txt](requirements.txt) is provided:
* pyinotify~=0.9.6
* pyudev~=0.22.0

Usage
-----
Usage is quite simple. By default, logs are printed to stdout

```bash
usage: python3 main.py [options]
  options:
    %file_name%, move output to file_name file
```