# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module contains the General entity class.

.. module:: general
    :synopsis: Contains the General entity class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from bGrease import Entity
from fife_rpg.components.general import General as GeneralComponent

class General(Entity):
    """The Base for all fife-rpg entities"""

    def __init__(self, world, identifier):
        """Constructor

        Args:
            world: The world the entity belongs to
            identifier: A unique identifier"""
        Entity.__init__(self, world)
        if not GeneralComponent.registered_as:
            GeneralComponent.register()
        getattr(self, GeneralComponent.registered_as).identifier = identifier
    
    @property
    def identifier(self):
        """Returns the identifier of the entity"""
        return getattr(self, GeneralComponent.registered_as).identifier
