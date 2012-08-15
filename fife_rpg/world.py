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
from fife.extensions.serializers.xmlobject import XMLObjectLoader
from fife.extensions.serializers.xml_loader_tools import loadImportDirRec
import yaml
from copy import copy

from fife_rpg.components import ComponentManager
from fife_rpg.systems import SystemManager
from fife_rpg.entities.rpg_entity import RPGEntity
from fife_rpg.systems import GameVariables
from fife_rpg.components.agent import Agent
from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg.components.general import General

class RPGWorld(World):
    """The Base world for all rpgs.
    
    Sets up the generic systems and components
    
    Properties:
        application: The :class:`fife_rpg.rpg_application.RPGApplication` that 
        uses this engine
        
        object_db: Stores the template data        
    """
    
    MAX_ID_NUMBER = 1000
    
    def __init__(self, application):
        World.__init__(self, application.engine)
        self.application = application
        self.object_db = {}
        registered_as = GameVariables.registered_as
        if registered_as and hasattr(self.systems, registered_as):
            environment = getattr(self.systems, registered_as) 
            environment.add_callback(self.update_game_variables)
        if not Agent.registered_as:
            Agent.register()
        if not FifeAgent.registered_as:
            FifeAgent.register()
        if not General.registered_as:
            General.register()
        yaml.add_representer(RPGEntity, self.entity_representer)
        yaml.add_constructor('!Entity', self.entity_constructor, yaml.SafeLoader)
                
    def get_entity(self, identifier):
        """Returns the entity with the identifier
        
        Args:
            identifier: The identifier of the entity
        
        Returns:
            The entity with the identifier or None
        """
        extent = getattr(self[RPGEntity], General.registered_as)
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
        if not General.registered_as:
            General.register()
    
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
           
            new_ent = RPGEntity(self, identifier)
            for component, data in info.items():
                comp_obj = getattr(new_ent, component)
                for key, value in data.items():
                    setattr(comp_obj, key, value)
            return new_ent
        else:
            return None
        
    def update_game_variables(self, variables):
        """Called by the game environment when it wants to update its globals
        
        Args:
            variables: The globals dictionary of the GameEnvironment that is 
            filled by the GameScene
        """
        extent = getattr(self[RPGEntity], General.registered_as)
        for entity in extent:            
            variables[entity.identifier] = entity
        
    def import_agent_objects(self, object_path=None):
        """Import the objects used by agents from the given path

        Args:
            object_path: The root path in which the objects are.
            If set to None it the path will be read from the settings
        """
        if not object_path:
            object_path = self.application.settings.get(
                "fife-rpg", "AgentObjectsPath", "objects/agents")
        engine = self.engine
        obj_loader = XMLObjectLoader(engine)
        loadImportDirRec(obj_loader, object_path, engine, True)

    def read_object_db(self, db_filename=None):
        """Reads the Object Information Database from a file

        Args:
            db_filename: The yaml file to read from. Overwrites the
            ObjectDBFile setting if not set to None.
        """
        if not db_filename:
            db_filename = self.application.settings.get(
                "fife-rpg", "ObjectDBFile", "objects/object_database.yaml")
        vfs = self.engine.getVFS()
        database_file = vfs.open(db_filename)
        database = yaml.load_all(database_file)
        for object_info in database:
            self.object_db.update(object_info)

    def update_from_template(self, entity_data, template_name):
        """Copies missing data from a template into an entity dictionary.

        Args:
            entity_data: The dictionary in which the data should be put.
            
            template_name: The name of the template to use

        Returns:
            The modified entity dictionary
        """
        if self.object_db.has_key(template_name):
            template_data = copy(self.object_db[template_name])
            for key in template_data.keys():
                if entity_data.has_key(key):                    
                    tmp_attributes = template_data[key]
                    tmp_attributes.update(entity_data[key])
                    entity_data[key] = tmp_attributes
                else:
                    entity_data[key] = template_data[key]
        return entity_data
    
    def load_and_create_entities(self, entities_file_name=None):
        """Reads the entities from a file and creates them
        
        Args:
            entities_file_name: The path to the entities file. Overwrites
            the EntitiesFile setting if not set to None
        """
        if not entities_file_name:
            entities_file_name = self.application.settings.get(
                "fife-rpg", "EntitiesFile", "objects/entities.yaml")
        vfs = self.engine.getVFS()
        entities_file = vfs.open(entities_file_name)
        entities = yaml.safe_load_all(entities_file)
        try:
            while entities.next():
                entities.next()
        except StopIteration:
            pass
        
    def create_entity_dictionary(self, entity):
        """Creates a dictionary containing the values of the Entity
        
        Args:
            entity: The Entity instance
        
        Returns:
            The created dictionary
        """
        entity_dict = {}
        components_data = entity_dict["components"] = {}
        components = ComponentManager.get_components()
        for name, component in components.iteritems():
            component_values = getattr(entity, name)
            if component_values:
                component_data = None
                for field in component.saveable_fields:                
                    if not component_data:
                        component_data = components_data[name] = {}                
                    component_data[field] = getattr(component_values, field)    
        return entity_dict

    def entity_representer(self, dumper, data):
        """Creates a yaml node representing an entity
        
        Args:
            dumper: A yaml BaseRepresenter
            
            data: The Entity
        
        Returns:
            The created node
        """
        entity_dict = self.create_entity_dictionary(data)
        entity_node = dumper.represent_mapping(u"!Entity", entity_dict)
        return entity_node
    
    def entity_constructor(self, loader, node):
        """Constructs an Entity from a yaml node
        
        Args:
            loader: A yaml BaseConstructor
            
            node: The yaml node
            
        Returns:
            The created Entity
        """
        entity_dict = loader.construct_mapping(node, deep=True)
        template = None
        if entity_dict.has_key("Template"):
            template = entity_dict["Template"]
        if entity_dict.has_key("Components"):
            components_data = entity_dict["Components"]
            if template:
                self.update_from_template(components_data, template)
            general_name = General.registered_as
            identifier = None
            if not components_data.has_key(general_name):
                identifier = self.create_unique_identifier(template)
            else:
                general_data = components_data[General.registered_as]
                identifier = general_data["identifier"]
            return self.get_or_create_entity(identifier, components_data)  
        elif template:
            components_data = {}
            self.update_from_template(components_data, template)
            identifier = self.create_unique_identifier(template)
            return self.get_or_create_entity(identifier, components_data)
        else:
            raise ValueError("There is no identifier and no Template set." 
                             "Can't create an Entity without an identifier.")
            
    def pump(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        World.pump(self, time_delta)
        checkers = ComponentManager.get_checkers()
        for names, callback in checkers:
            for components in self.components.join(*names):
                callback(*components)
