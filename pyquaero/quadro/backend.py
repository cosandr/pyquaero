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

import threading
from datetime import datetime

from .usb import get_device


class Backend:
    """Backend that connects to the Quadro device and offers a set of mid level
    operations.

    This class is threadsafe. Multiple threads can share a Backend instance.
    """

    def __init__(self, unit=0):
        """Create a new Backend instance that is connected to the given Quadro unit."""
        self.lock = threading.Lock()
        self.device = get_device(unit)
        self.last_status_ts = None
        self._expected_length = 188  # FW >= 1018

    def close(self):
        """Close the Backend, releasing all resources. Must be invoked!"""
        self.device.close()

    def read_status(self, length, max_age=0.0):
        """Read the current status.

        The last status is cached. If it is younger than max_age (in seconds), the cached
        status is returned instead.
        """
        with self.lock:
            if (self.last_status_ts is None or
                    (datetime.now() - self.last_status_ts).total_seconds() >= max_age):
                status = self.device.read_endpoint(length, endpoint=2)
                # Sometimes fails, returning partial data
                if len(status) < self._expected_length:
                    # The next request contains the remaining data
                    status += self.device.read_endpoint(length, endpoint=2)
                self._cache_status(status)
            return self.last_status

    def _cache_status(self, status):
        """Cache a status."""
        self.last_status = status
        self.last_status_ts = datetime.now()

    def read_settings(self, length):
        """Read the current settings."""
        with self.lock:
            return self.device.receive_report(11, length)

    def get_firmware(self):
        """Get the firmware version of the Quadro at the given AquaDevice."""
        from pyquaero.struct.type import Group, UnsignedWord
        with self.lock:
            status = self.read_status(self._expected_length, max_age=1)
        scheme = Group(scheme={'firmware_version': UnsignedWord(at=0x000d)})
        return scheme.get(status)['firmware_version']

    def get_structure(self):
        """Get the structure version of the Quadro at the given AquaDevice."""
        from pyquaero.struct.type import Group, UnsignedWord
        with self.lock:
            status = self.read_status(self._expected_length, max_age=1)
        scheme = Group(scheme={'structure_version': UnsignedWord(at=0x0001)})
        return scheme.get(status)['structure_version']
