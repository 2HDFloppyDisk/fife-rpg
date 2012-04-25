# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The Graphics component and functions

.. module:: graphics
    :synopsis: The Graphics component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class Graphics(Base):
    """Component that stores the values for the graphical representation"""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, gfx=str)

    @classmethod
    def register(cls, name="graphics"):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Graphics, cls).register(name))
