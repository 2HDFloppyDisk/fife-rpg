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

"""The Dialogue component and functions

.. module:: dialogue
    :synopsis: The Dialogue component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife_rpg.components.base import Base


class Dialogue(Base):
    """Component that stores the dialogue

    Fields:
        dialogue: Either a |Dialogue| object, or a dictionary containing the
        data for a |Dialogue| or a string that points to a dialogue file.
    """

    def __init__(self):
        Base.__init__(self, dialogue=object)

    @classmethod
    def register(cls, name="Dialogue", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return super(Dialogue, cls).register(name, auto_register)
