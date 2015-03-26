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

"""The Containable component and functions

.. module:: containable
    :synopsis: The Containable component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base


class Containable(Base):

    """Component that allows an entity to be contained by Container entity.

    Fields:
        bulk: How much space the containable uses

        weight: The weight of the containable

        item_Type: What type the containable item is

        image: The image that is displayed in inventories

        container: The container in which the containable currently is

        slot: The slot in which the containable currently is
    """

    def __init__(self):
        Base.__init__(self, bulk=int, weight=int, item_type=str, image=str,
                      container=object, slot=int)

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        return fields

    @classmethod
    def register(cls, name="Containable", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return super(Containable, cls).register(name, auto_register)
