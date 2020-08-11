#
# pyquaero - a Python library for Aquaero fan controllers
#
# Copyright (C) 2020 Andrei Costescu
#   https://github.com/cosandr/pyquaero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Andrei Costescu'

import time
from contextlib import contextmanager
from typing import List

import pywinusb.hid as hid


VENDOR_ID = 0x0c70
PRODUCT_ID = 0xf00d


@contextmanager
def use_device(dev: hid.HidDevice):
    if not dev.is_opened():
        dev.open()
    try:
        yield dev
    finally:
        dev.close()


class QuadroDevice(object):
    """Quadro USB device object.

    Connect to the Quadro via USB and offer a set of low level access methods that
    are firmware independent.
    """

    def __init__(self, dev):
        """Initialize the AquaDevice object."""
        self.dev: hid.HidDevice = dev
        self.dev.open()
        self.dev.set_raw_data_handler(self.read_handler)
        self.last_data = None

    def read_handler(self, data):
        self.last_data = bytes(data)

    def close(self):
        """Close the AquaDevice object after usage.

        Must be invoked to properly release the USB device!
        """
        self.dev.close()

    def read_endpoint(self, length, endpoint):
        """Reads a number of data from the given endpoint."""
        while not self.last_data:
            time.sleep(0.5)
        return self.last_data


def count_devices():
    """Count the number of Aquaero devices found."""
    devices = []
    hid_devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
    for hd in hid_devices:
        with use_device(hd) as dev:
            if dev.find_output_reports():
                devices.append(dev)
    return len(devices)


def get_device(unit=0):
    """Return an AquaDevice instance for the given Aquaero device unit found."""
    devices = []
    hid_devices: List[hid.HidDevice] = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
    for hd in hid_devices:
        with use_device(hd) as dev:
            if dev.find_output_reports():
                devices.append(dev)
    if unit >= len(devices):
        raise IndexError('No Aquaero unit %d found' % unit)
    return QuadroDevice(devices[unit])
