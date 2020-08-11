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

from pyquaero import quadro


class Quadro:
    """Main class for communication with a Quadro device.

    Its intention is to return an easy to use API and hide all firmware and communication
    related stuff from the invoker.
    """

    def __init__(self, unit=0):
        """Create a new Quadro instance for the given unit."""
        self.backend = quadro.backend.Backend(unit)
        self.firmware = self.backend.get_firmware()
        self.structure = self.backend.get_structure()
        self.serializer = quadro.create_serializer(self.structure, self.firmware)

    def __enter__(self):
        return self

    def __exit__(self, exType, exValue, exTrackback):
        self.close()

    def close(self):
        """Close the Quadro connection, releasing all resources. Must be invoked."""
        self.backend.close()

    def get_status(self):
        """Get the current status of the Quadro device."""
        status = self.serializer.read_status(self.backend)
        return self.serializer.unpack_status(status)
