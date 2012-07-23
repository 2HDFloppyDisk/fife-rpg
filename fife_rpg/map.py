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

"""This module contains everything for handling fife-rpg maps

.. module:: map
    :synopsis: contains everything for handling fife-rpg maps.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg.components.agent import Agent
from fife_rpg.components.general import General

class NoSuchRegionError(Exception):
    """Gets thrown when the code tried to access a region that does not exits 
    on the map."""

    def __init__(self, map_name, region_name):
        """Constructor

        Args:
            map_name: The name of the map_name
            region_name: The name of the region_name
        """
        Exception.__init__(self)
        self.map = map_name
        self.region = region_name

    def __str__(self):
        """Returns a string representing the exception"""
        return ("The map '%s' has no region called '%s'." % 
                    (self.map,  self.region))

class Map(object):
    """Contains the data of a map"""

    def __init__(self, fife_map, name, camera, actor_layer, 
                 ground_object_layer, item_layer, regions):
        """Constructor

        Args:
            fife_map: A fife.Map instance, representing the fife_map
            name: The name of the fife_map.
            camera: The name of the default camera
            actor_layer: The name of the actor layer
            ground_object_layer: The name of the ground object layer
            item_layer: The name of the item layer
            regions: A dictionary that defines specific regions on the fife_map, as
            fife.DoubleRect instances.
        """
        self.__map = fife_map
        self.__name = name
        self.__regions = regions
        self.__entities = {}
        self.__camera = fife_map.getCamera(camera)
        self.__actor_layer = fife_map.getLayer(actor_layer)
        self.__ground_object_layer = fife_map.getLayer(ground_object_layer)
        self.__item_layer = fife_map.getLayer(item_layer)
        if not FifeAgent.registered_as:
            FifeAgent.register()
        if not Agent.registered_as:
            Agent.register()
        if not General.registered_as:
            General.register()

    @property
    def map(self):
        """Returns the fife.Map"""
        return self.__map

    @property
    def name(self):
        """Returns the name of the map"""
        return self.__name

    @property
    def regions(self):
        """Returns the regions of the map"""
        return self.__regions

    @property
    def entities(self):
        """Returns the entities that are on this map"""
        return self.__entities

    @property
    def camera(self):
        """Returns the camera of the map"""
        return self.__camera

    @property
    def actor_layer(self):
        """Returns the agent layer of the map"""
        return self.__actor_layer

    @property
    def ground_object_layer(self):
        """Returns the ground object layer of the map"""
        return self.__ground_object_layer

    @property
    def item_layer(self):
        """Returns the item layer of the map"""
        return self.__item_layer

    @property
    def is_active(self):
        """Returns wheter the map is active or not"""
        return self.camera.isEnabled()

    def __getitem__(self, name):
        """Returns the entity with the given name
        
        Args:
            name: The name of the entity
            
        Raises:
            KeyError: If the map has no entity with that name
            TypeError: If the key is not a string
        """
        if not type(name) == str:
            raise TypeError("Expected key to be a string")
        for entity in self.entities:
            general = getattr(entity, General.registered_as)
            if general.identifier == name:
                return entity
        raise KeyError("The map %s has no entity with the name %s" % 
                       (self.name, name))
    
    def get_instances_at(self, point, layer):
        """Query the main camera for instances on the specified layer.
        
        Args:
            point: The point that should be checked
            layer: The layer from which we want the instances 
        """
        return self.camera.getMatchingInstances(point, layer)
    
    def is_in_region(self, location, region):
        """Checks if a given point is inside the given region

        Args:
            location: A fife.DoublePoint instance
            region: The name of the region

        Raises:
            NoSuchRegionError: The specified region does not exist.
        """
        if not region in self.regions:
            raise NoSuchRegionError(self.name,  region)
        else:
            return self.regions[region].contains(location)

    def activate(self):
        """Activates the map"""
        self.camera.setEnabled(True)

    def deactivate(self):
        """Deactivates the map"""
        self.camera.setEnabled(False)
        
    def update_entities(self, world):
        """Update the maps entites from the entities of the world
        
        Args:
            world: The world on which the map looks for its entities
        """
        extent = world[...]
        self.__entities = getattr(extent, 
                                  Agent.registered_as).map == self.name
        
    def update_entitities_agent(self):
        """Update the values of the agent component of the maps entities"""
        for entity in self.entities:
            if hasattr(entity, FifeAgent.registered_as):
                fifeagent = getattr(entity, FifeAgent.registered_as)
                agent = getattr(entity, Agent.registered_as)
                location = fifeagent.behaviour.location
                agent.position = (location.x, location.y, location.z)
                agent.rotation = fifeagent.behaviour.rotation
                
    def remove_entity(self, identifier):
        """Removes an entity from the map
        
        Args:
            identifier: The name of the entity
        
        Raises:
            KeyError: If the map has no entity with that name
            TypeError: If the identifier is not a string
        """
        try:
            entity = self[identifier]
            fifeagent = getattr(entity, FifeAgent.registered_as)
            instance = fifeagent.layer.getInstance(identifier)
            fifeagent.layer.deleteInstance(instance)
            delattr(entity, FifeAgent.registered_as)
            agent = getattr(entity, Agent.registered_as)
            agent.map = None
        except KeyError as error:
            raise error
        except TypeError as error:
            raise TypeError("Expected identifier to be a string")
