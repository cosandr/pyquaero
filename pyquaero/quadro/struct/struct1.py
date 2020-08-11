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

from pyquaero.struct import AquaSerializer
from pyquaero.struct.type import *


class Uptime(UnsignedLong):
    """An uptime as datetime.timedelta."""
    def fetch(self, data, pos):
        val = UnsignedLong.fetch(self, data, pos)
        return datetime.timedelta(seconds=val/10)


class QuadroSerializer1(AquaSerializer):
    """An AquaSerializer for Quadro firmware version lower than 1018."""
    # UNTESTED
    # Many thanks to Martin from HWiNFO for sharing his findings
    status_scheme = Group(scheme={
        'structure_version':    UnsignedWord(at=0x01),
        'serial_major':         UnsignedWord(at=0x03),
        'serial_minor':         UnsignedWord(at=0x05),
        'bootloader_version':   UnsignedWord(at=0x07),
        'hardware_version':     UnsignedWord(at=0x0b),
        'firmware_version':     UnsignedWord(at=0x0d),
        'uptime':               Uptime(at=0x14),  # Unknown
        'temperatures':         Group(scheme={
            'sensor':               Array(items=4, scheme={
                 'temp':                Temperature(at=0x34, step=2),
                                    }),
            'software':             Array(items=8, scheme={
                 'temp':                Temperature(at=0x3c, step=2),
                                    }),
                                }),
        'units':                Group(scheme={
            'software':             Array(items=8, scheme={
                'temperature':          Mapped(at=0x50, step=1, values={
                                            0: 'celsius',
                                            1: 'fahrenheit',
                                            2: 'kelvin',
                                        }),
                                    }),
                                }),
        'vcc12':                Fraction(at=0x58, divisor=100.0),
        'flow_meters':          Array(items=1, scheme={
            'rate':                 Fraction(divisor=10.0, at=0x5a, step=2, optional=True),
                                }),
        'fans':                 Array(items=4, scheme={
            'duty':                 Percent(at=0x5c, step=13),
            'voltage':              Fraction(at=0x5e, step=13, divisor=100.0),
            'power':                UnsignedWord(at=0x62, step=13),
            'speed':                UnsignedWord(at=0x64, step=13, optional=True),
        }),
    })

    def read_status(self, backend):
        # Might be 164
        return backend.read_status(154, max_age=1)

    def unpack_status(self, data):
        return self.status_scheme.get(data)
