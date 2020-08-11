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

import platform
import usb


VENDOR_ID = 0x0c70
PRODUCT_ID = 0xf00d


class QuadroDevice(object):
    """Quadro USB device object.

    Connect to the Quadro via USB and offer a set of low level access methods that
    are firmware independent.
    """

    def __init__(self, dev):
        """Initialize the AquaDevice object."""
        self.dev = dev
        self.interface = [self.dev[0][(x, 0)] for x in range(2)]

        if platform.system() == "Windows":
            return
        # claim the interfaces if held by the kernel
        for intf in self.interface:
            if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                self.dev.detach_kernel_driver(intf.bInterfaceNumber)
                usb.util.claim_interface(self.dev, intf)

    def close(self):
        """Close the AquaDevice object after usage.

        Must be invoked to properly release the USB device!
        """
        if platform.system() == "Windows":
            return
        for intf in self.interface:
            try:
                usb.util.release_interface(self.dev, intf)
                self.dev.attach_kernel_driver(intf.bInterfaceNumber)
            except usb.core.USBError as e:
                if e.errno == 2:
                    continue
                raise

    def receive_report(self, reportId, length, wIndex=1):
        """Send a USBHID IN report request to the AquaDevice and receive the answer."""
        return self.dev.ctrl_transfer(bmRequestType=0xa1, bRequest=0x01,
                               wValue=(0x0300 | reportId), wIndex=wIndex,
                               data_or_wLength=length)

    def read_endpoint(self, length, endpoint):
        """Reads a number of data from the given endpoint."""
        ep = self.interface[endpoint - 1][0]
        return ep.read(length)


def count_devices():
    """Count the number of Quadro devices found."""
    devices = list(usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, find_all=True))
    return len(devices)


def get_device(unit=0):
    """Return a QuadroDevice instance for the given Quadro device unit found."""
    devices = list(usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, find_all=True))
    if unit >= len(devices):
        raise IndexError('No Aquaero unit %d found' % unit)
    return QuadroDevice(devices[unit])
