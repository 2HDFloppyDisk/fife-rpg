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
from builtins import next
from builtins import str
from copy import copy
import sys
import imp

from bGrease.grease_fife.world import World, WorldEntitySet, EntityExtent
from fife.fife import MapLoader
import yaml

from fife_rpg import helpers
from fife_rpg.components import ComponentManager
from fife_rpg.systems import SystemManager
from fife_rpg.entities.rpg_entity import RPGEntity
from fife_rpg.systems import GameVariables
from fife_rpg.components.agent import Agent
from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg.components.general import General


class RPGWorldEntitySet(WorldEntitySet):

    """Specialized World entity set"""

    def remove(self, entity):
        self.world.on_entity_delete(entity)
        WorldEntitySet.remove(self, entity)


class RPGWorld(World):

    """The Base world for all rpgs.

    Sets up the generic systems and components

    Properties:
        application: The :class:`fife_rpg.rpg_application.RPGApplication` that
        uses this engine

        object_db: Stores the template data
    """

    MAX_ID_NUMBER = sys.maxsize

    def __init__(self, application):
        self.application = application
        self.object_db = {}
        GameVariables.add_callback(self.update_game_variables)
        self.register_mandatory_components()
        yaml.add_representer(RPGEntity, self.entity_representer,
                             yaml.SafeDumper)
        yaml.add_constructor('!Entity', self.entity_constructor,
                             yaml.SafeLoader)
        yaml.add_representer(helpers.DoublePointYaml,
                             helpers.double_point_representer,
                             yaml.SafeDumper)
        yaml.add_constructor("!DoublePoint",
                             helpers.double_point_constructor,
                             yaml.SafeLoader)
        yaml.add_representer(helpers.DoublePoint3DYaml,
                             helpers.double_point_3d_representer,
                             yaml.SafeDumper)
        yaml.add_constructor("!DoublePoint3D",
                             helpers.double_point_3d_constructor,
                             yaml.SafeLoader)
        World.__init__(self, application.engine)
        self.entities = RPGWorldEntitySet(self)
        self._full_extent = EntityExtent(self, self.entities)
        self._entity_delete_callbacks = set()
        self.__entity_cache = {}

    def register_mandatory_components(self):
        """Registers the mandatory components"""
        if not Agent.registered_as:
            Agent.register()
        if not FifeAgent.registered_as:
            FifeAgent.register()
        if not General.registered_as:
            General.register()

    def get_entity(self, identifier):
        """Returns the entity with the identifier

        Args:
            identifier: The identifier of the entity

        Returns:
            The entity with the identifier or None
        """
        if self.is_identifier_used(identifier):
            return self.__entity_cache[identifier]
        return None

    def is_identifier_used(self, identifier):
        """Checks whether the idenfier is used

        Args:
            identifier: The identifier to check

        Returns:
            True if the identifier is used, false if not
        """
        return identifier in self.__entity_cache

    def create_unique_identifier(self, identifier):
        """Returns an unused identifier based on the given identifier

        Args:
            identifier: The base identifier

        Returns:
            A unique unused identifier based in the given identifier
        """
        if not self.is_identifier_used(identifier):
            return identifier
        id_number = 1
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
        for name, component in components.items():
            setattr(self.components, name, component)
        systems = SystemManager.get_systems()
        for name, system in systems.items():
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

            for key, val in list(extra.items()):
                info[key].update(val)

            new_ent = RPGEntity(self, identifier)
            for component, data in list(info.items()):
                setattr(new_ent, component, None)
                comp_obj = getattr(new_ent, component)
                for key, value in list(data.items()):
                    setattr(comp_obj, key, value)
            self.__entity_cache[identifier] = new_ent
            return new_ent
        else:
            return None

    def update_game_variables(self, variables):
        """Called by the game environment when it wants to update its globals

        Args:
            variables: The globals dictionary of the GameEnvironment that is
            filled by the GameScene
        """
        ent_module = imp.new_module("entities")
        extent = getattr(self[RPGEntity], General.registered_as)
        for entity in extent:
            ent_module.__dict__[entity.identifier] = entity
        variables["entities"] = ent_module

    def import_agent_objects(self, object_path=None):
        """Import the objects used by agents from the given path

        Args:
            object_path: The root path in which the objects are.
            If set to None it the path will be read from the settings
        """
        if not object_path:
            object_path = self.application.settings.get(
                "fife-rpg", "AgentObjectsPath", "objects/agents")
        loader = MapLoader(self.engine.getModel(),
                           self.engine.getVFS(),
                           self.engine.getImageManager(),
                           self.engine.getRenderBackend())
        loader.loadImportDirectory(object_path)

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
        if template_name in self.object_db:
            template_data = copy(self.object_db[template_name])
            for key in list(template_data.keys()):
                if key in entity_data:
                    tmp_attributes = template_data[key].copy()
                    tmp_attributes.update(entity_data[key])
                    entity_data[key] = tmp_attributes
                else:
                    entity_data[key] = template_data[key].copy()
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
            while next(entities):
                next(entities)
        except StopIteration:
            pass

    @classmethod
    def create_entity_dictionary(cls, entity, remove_default=True):
        """Creates a dictionary containing the values of the Entity

        Args:
            entity: The Entity instance

            remove_default: Skips fields whose value is the same as the
            default value.

        Returns:
            The created dictionary
        """
        entity_dict = {}
        components_data = entity_dict["Components"] = {}
        components = ComponentManager.get_components()
        for name, component in components.items():
            component_values = getattr(entity, name)
            if component_values:
                component_data = None
                for field in component.saveable_fields:
                    fields = component.fields
                    if not component_data:
                        component_data = components_data[name] = {}
                    value = getattr(component_values, field)
                    if remove_default and value == fields[field].default():
                        continue
                    component_data[field] = value
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
        if "Template" in entity_dict:
            template = entity_dict["Template"]
        if "Components" in entity_dict:
            components_data = entity_dict["Components"]
            if template:
                self.update_from_template(components_data, template)
            general_name = General.registered_as
            identifier = None
            if general_name not in components_data:
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

    def clear(self):
        """Clear the world, remove all entities"""
        self.object_db = {}

    def add_entity_delete_callback(self, func):
        """Adds a callback to the entity delete callbacks"""
        self._entity_delete_callbacks.add(func)

    def on_entity_delete(self, entity):
        """Calls the callbacks for deletion of an entity.

        Args:

            entity:
                The entity that should be deleted.
        """
        del self.__entity_cache[entity.identifier]
        for callback in self._entity_delete_callbacks:
            callback(entity)

    def rename_entity(self, old_identifier, new_identifier):
        """Renames an entity. The new name will be ran through
        create_unique_identifier before applying.

        Args:
            old_identifier: The pöd name of the entity

            new_identifier: The new name of the entity.

        Returns:
            The actual new name of the entity.
        """
        if not self.is_identifier_used(old_identifier):
            raise ValueError("There is no \"{}\" entity".format(old_identifier))
        entity = self.get_entity(old_identifier)
        new_identifier = self.create_unique_identifier(new_identifier)
        del self.__entity_cache[old_identifier]
        comp_data = getattr(entity, General.registered_as)
        setattr(comp_data, "identifier", new_identifier)
        self.__entity_cache[new_identifier] = entity
        return new_identifier


    def step(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        World.step(self, time_delta)
        checkers = ComponentManager.get_checkers()
        for names, callback in checkers:
            for components in self.components.join(*names):
                callback(*components)
