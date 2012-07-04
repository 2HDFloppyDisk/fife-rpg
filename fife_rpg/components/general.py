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

"""The General component and functions

.. module:: general
    :synopsis: The General component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife_rpg.components.base import Base

class General(Base):
    """Component that stores the general values of an parpg entity"""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, identifier=str)

    @classmethod
    def register(cls, name="general", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(General, cls).register(name, auto_register))
