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


def create_serializer(structure, firmware):
    """Create an AquaSerializer instance for the given structure and firmware version."""
    if structure < 3 and firmware < 1018:
        from .struct1 import QuadroSerializer1
        return QuadroSerializer1()
    if structure >= 3 and firmware >= 1018:
        from .struct3 import QuadroSerializer3
        return QuadroSerializer3()

    raise LookupError('firmware version %d (structure version %d) is not supported' % (firmware, structure))
