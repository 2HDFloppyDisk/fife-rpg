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

"""The Usable component and functions

.. module:: usable
    :synopsis: The Usable component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class Usable(Base):
    """
    Component that stores data about the actions that an object can do.
    """

    def __init__(self):
        Base.__init__(self, actions=dict)

    @classmethod
    def register(cls, name="usable"):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Usable, cls).register(name))
