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
#
# This module is based on the PARPGWorld class.

"""This module contains the world class used used by the entity system.

.. module:: world
    :synopsis: Contains the world class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from bGrease.grease_fife.world import World

from fife_rpg.components import ComponentManager
from fife_rpg.systems import SystemManager
from fife_rpg.entities.general import General
from fife_rpg.components.general import General as GeneralComponent

class RPGWorld(World):
    """The Base world for all rpgs.
    
    Sets up the generic systems and components"""
    
    MAX_ID_NUMBER = 1000
    
    def __init__(self, engine):
        """Constructor

        Args:
            engine: a fife.Engine instance
        """
        World.__init__(self, engine)
    
    def get_entity(self, identifier):
        """Returns the entity with the identifier
        
        Args:
            identifier: The identifier of the entity
        
        Returns:
            The entity with the identifier or None
        """
        extent = getattr(self[General], GeneralComponent.registered_as)
        entities = extent.identifier == identifier
        if len(entities) > 0:
            return entities.pop()
        return None

    def is_identifier_used(self, identifier):
        """Checks whether the idenfier is used
        
        Args:
            identifier: The identifier to check
        
        Returns:
            True if the identifier is used, false if not
        """
        entity = self.get_entity(identifier) 
        return not entity is None    
    
    def create_unique_identifier(self, identifier):
        """Returns an unused identifier based on the given identifier
        
        Args:
            identifier: The base identifier
        
        Returns:
            A unique unused identifier based in the given identifier
        """
        id_number = 0
        while self.is_identifier_used(identifier + "_" + str(id_number)):
            id_number += 1
            if id_number > self.MAX_ID_NUMBER:
                raise ValueError(
                    "Number exceeds MAX_ID_NUMBER:" + 
                    str(self.MAX_ID_NUMBER)
                )
        identifier = identifier + "_" + str(id_number)
        return identifier
    
    def configure(self):
        """Configure the worlds components and systems"""
        World.configure(self)
        components = ComponentManager.get_components()
        for name, component in components.iteritems():
            setattr(self.components, name, component)
        systems = SystemManager.get_systems()
        for name, system in systems.iteritems():
            setattr(self.systems, name, system)
        if not GeneralComponent.registered_as:
            GeneralComponent.register()
    
    def get_or_create_entity(self, identifier, info=None, extra=None):
        """Create an entity if not already present and return it.
        
            Args:
                identifier: The identifier of the new object
                info: Stores information about the object we want to create
                extra: Stores additionally required attributes
        
            Returns:
                The entity with the identifier.
                None: If there is no info dictionary and no entity with the
                identifier
           """
        if self.is_identifier_used(identifier):
            return self.get_entity(identifier)
        elif info is not None:
            extra = extra or {}
            
            for key, val in extra.items():
                info[key].update(val)      
           
            new_ent = General(self, identifier)
            for component, data in info.items():
                comp_obj = getattr(new_ent, component)
                for key, value in data.items():
                    setattr(comp_obj, key, value)
            return new_ent
        else:
            return None 
