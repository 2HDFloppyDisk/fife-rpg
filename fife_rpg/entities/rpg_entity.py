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
"""This module contains the RPGEntity entity class.

.. module:: general
    :synopsis: Contains the RPGEntity entity class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from bGrease import Entity

from fife_rpg.components.general import General
from fife_rpg.exceptions import AlreadyRegisteredError

class RPGEntity(Entity):
    """The Base for all fife-rpg entities
        
    Properties:
            world: The world the entity belongs to. 
            A :class:`fife_rpg.world.RPGWorld`
            
            identifier: A unique identifier
    """

    def __init__(self, world, identifier):

        Entity.__init__(self, world)
        if not General.registered_as:
            General.register()
        getattr(self, General.registered_as).identifier = identifier
    
    @property
    def identifier(self):
        """Returns the identifier of the entity"""
        return getattr(self, General.registered_as).identifier

def set_component_value(entity, component, field, value):
    """Sets the field value of an entities component to the specified value
    
    Args:
        entity: A :class:`fife_rpg.entities.rpg_entity.RPGEntity`
        
        component: The name of the component
        
        field: The field of the component
        
        value: The value to which the field is set
    """
    component_data = getattr(entity, component)
    setattr(component_data, field, value)
    
try:
    from fife_rpg.console_commands import register_command
    register_command("SetComponentValue", lambda application, entity_name, *args:
                     set_component_value(application.world.get_entity(entity_name),
                                         *args))
except AlreadyRegisteredError:
    pass    