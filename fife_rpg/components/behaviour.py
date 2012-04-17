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

"""The Behaviour component and functions

.. module:: behaviour
    :synopsis: The Behaviour component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class Behaviour(Base):
    """Component that stores the values of the behaviour"""

    __registered_as = ""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, behaviour_type=str)
        self.behaviour_type = "Base"

    @classmethod
    def register(cls, name="behaviour"):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the component was registered, False if not.
        """

        if (super(Behaviour, cls).register(name)):
            cls.__registered_as = name
            return True
        return False
