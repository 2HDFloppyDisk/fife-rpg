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

"""The Description component and functions

.. module:: description
    :synopsis: The Description component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
from fife_rpg.components.base import Base


class Description(Base):
    """Component that stores the description of an object

    Fields:
        view_name: The displayed name of the entity

        real_name: The real name of the entity

        desc: Text describing the entity
        """

    def __init__(self):
        Base.__init__(self, view_name=str, real_name=str, desc=str)

    @classmethod
    def register(cls, name="Description", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return super(Description, cls).register(name, auto_register)
