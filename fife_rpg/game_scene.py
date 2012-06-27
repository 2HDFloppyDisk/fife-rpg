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
# This package is based on the gamescene classes of PARPG

"""This module contains the generic controller and view to display a
fife_rpg map.

.. module:: controllers
    :synopsis: The generic controller and view to display a
fife_rpg map.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import os
from copy import copy 

from fife import fife
from fife.extensions.loaders import loadMapFile
from fife.extensions.serializers.xmlobject import XMLObjectLoader
from fife.extensions.serializers.xml_loader_tools import loadImportDirRec
import yaml

from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg import Map
from fife_rpg import ViewBase
from fife_rpg import ControllerBase
from fife_rpg import RPGWorld
from fife_rpg.components.agent import Agent
from fife_rpg.components.fifeagent import FifeAgent, setup_behaviour
from fife_rpg.components.general import General
from fife_rpg import behaviours as BehaviourManager
from fife_rpg.systems import GameEnvironment

class GameSceneListener(fife.IMouseListener):
    """The game listener.

    Handle mouse events in relation
    with game process.
    """

    def __init__(self, engine, gamecontroller):
        """Constructor

        Args:
            engine: The FIFE engine
            gamecontroller: The GameSceneController
        """
        self.engine = engine
        self.gamecontroller = gamecontroller

        self.eventmanager = self.engine.getEventManager()

        fife.IMouseListener.__init__(self)

    def mousePressed(self, event): # pylint: disable-msg=C0103,W0221
        """Called when a mouse button was pressed.

        Args:
            event: The mouse event
        """
        pass

    def mouseMoved(self, event): # pylint: disable-msg=C0103,W0221
        """Called when the mouse was moved.

        Args:
            event: The mouse event
        """
        pass

    def mouseReleased(self, event): # pylint: disable-msg=C0103,W0221
        """Called when a mouse button was released.

        Args:
            event: The mouse event
        """
        pass

    def mouseDragged(self, event): # pylint: disable-msg=C0103,W0221
        """Called when the mouse is moved while a button is being pressed.

        Args:
            event: The mouse event
        """
        pass

class GameSceneView(ViewBase):
    """The view responsible for showing the in-game gui"""

    def __init__(self, engine, controller=None):
        """Constructor

        Args:
            engine: The FIFE engine
            controller: The GameSceneController
        """
        ViewBase.__init__(self, engine,  controller)

class GameSceneController(ControllerBase, RPGWorld):
    """Handles the input for a game scene"""

    def __init__(self, view, application):
        """Constructor

        Args:
            view: The GameSceneView
            application: The RPGApplication
        """
        ControllerBase.__init__(self, view, application)
        RPGWorld.__init__(self, self.engine)
        self.__maps = {}
        self.__current_map = None
        self.object_db = {}
        registered_as = GameEnvironment.registered_as
        if registered_as and hasattr(self.systems, registered_as):
            environment = getattr(self.systems, registered_as) 
            environment.add_callback(self.update_environment)
        if not Agent.registered_as:
            Agent.register()
        if not FifeAgent.registered_as:
            FifeAgent.register()
        if not General.registered_as:
            General.register()

    @property
    def current_map(self):
        """Returns the current active map"""
        return self.__current_map

    @property
    def maps(self):
        """Returns a copy of the maps dictionary"""
        return copy(self.__maps)

    def update_environment(self, environment_globals):
        """Called by the game environment when it wants to update its globals
        
        Args:
            globals: The globals dictionary of the GameEnvironment that is 
            filled by the GameScene
        """
        environment_globals.update(self.maps)
        environment_globals["current_map"] = self.current_map 

    def add_map(self, name, filename_or_map):
        """Adds a map to the maps dictionary.
        
        Args:
            name: The name of the map
            filename_or_map: The file name map, without the extension,
            or a Map instance.
        """
        if not name in self.__maps:
            self.__maps[name] = filename_or_map
        else:
            raise AlreadyRegisteredError(name, "Map")

    def load_map(self, name):
        """Load the map with the given name

        Args:
            name: The name of the map to load
        """
        if name in self.__maps:
            game_map = self.__maps[name]
            if not isinstance(game_map, Map):
                use_lighting = self.application.settings.get(
                    "fife-rpg", "UseLighting", False)
                maps_path = self.application.settings.get(
                    "fife-rpg", "MapsPath", "maps")
                grid_type = self.application.settings.get(
                    "fife-rpg", "GridType", "square")
                grid_type = (self.application.engine.getModel().
                                getCellGrid(grid_type)
                             )
                camera = self.application.settings.get(
                    "fife-rpg", "Camera", "main")
                agent_layer = self.application.settings.get(
                "fife-rpg", "AgentLayer", "agents")
                fife_map = loadMapFile(os.path.join(
                                            maps_path, game_map + '.xml'),
                                       self.engine, extensions = {
                                            'lights': use_lighting})
                found_layer = False
                for layer in fife_map.getLayers():
                    if layer.getId() == agent_layer:
                        found_layer = True
                        break                
                    
                if not found_layer:
                    fife_map.createLayer(agent_layer, grid_type)
                #TODO: (Beliar) Add loading of additional objects, like regions
                #TODO: and entities
                regions = {}
                game_map = Map(fife_map, name, camera, agent_layer,
                                        regions)
                renderer = fife.InstanceRenderer.getInstance(game_map.camera)
                renderer.addActiveLayer(game_map.agent_layer)
                game_map.update_entities(self)
                object_namespace = self.application.settings.get("fife-rpg", 
                        "ObjectNamespace", "fife-rpg")
                fife_model = self.application.engine.getModel()
                for entity in game_map.entities:
                    agent = getattr(entity, Agent.registered_as)
                    map_object = fife_model.getObject(agent.gfx,
                                                     object_namespace)
                    general = getattr(entity, General.registered_as)
                    fife_instance = game_map.agent_layer.createInstance(
                                        map_object,
                                        fife.ExactModelCoordinate(agent.pos_x,
                                                                  agent.pos_y,
                                                                  agent.pos_z),
                                        general.identifier)
                    fife_instance.setRotation(agent.rotation)
                    visual = fife.InstanceVisual.create(fife_instance)
                    visual.setStackPosition(agent.stack_position)

                    if (map_object.getAction('default')):
                        target = fife.Location(game_map.agent_layer)
                        fife_instance.act('default', target, True)
                    
                    behaviour = BehaviourManager.get_behaviour(
                                            entity.behaviour.behaviour_type)()
                    behaviour.agent = fife_instance
                    fifeagent = getattr(entity, FifeAgent.registered_as)
                    fifeagent.behaviour = behaviour
                    fifeagent.layer = game_map.agent_layer
                    setup_behaviour(fifeagent)
                    fifeagent.behaviour.idle()
                    self.__maps[name] = game_map
        else:
            raise LookupError("The map with the name '%s' cannot be found"
                              %(name))
                
    def switch_map(self, name):
        """Switches to the given map.

        Args:
            name: The name of the map
        """
        if name in self.__maps:
            self.load_map(name)
            if self.__current_map:
                self.__current_map.deactivate()
            self.__current_map = self.maps[name]
            self.__current_map.activate()
        else:
            raise LookupError("The map with the name '%s' cannot be found" 
                        %(name))

    def load_maps(self):
        """Load the names of the available maps from a map file."""
        self.__maps = {}
        maps_path = self.application.settings.get(
            "fife-rpg", "MapsPath", "maps")
        vfs = self.application.engine.getVFS()
        maps_file = vfs.open(os.path.join(maps_path, "maps.yaml"))
        maps_doc = yaml.load(maps_file)
        for name, filename in maps_doc["Maps"].iteritems():
            self.add_map(name, filename)

    def import_agent_objects(self, object_path=None):
        """Import the objects used by agents from the given path

        Args:
            object_path: The root path in which the objects are.
            If set to None it the path will be read from the settings
        """
        if not object_path:
            object_path = self.application.settings.get(
                "fife-rpg", "AgentObjectsPath", "objects/agents")
        engine = self.application.engine
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
        vfs = self.application.engine.getVFS()
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
        vfs = self.application.engine.getVFS()
        entities_file = vfs.open(entities_file_name)
        entities = yaml.load_all(entities_file)
        for entity in entities:
            identifier = entity.keys()[0]
            entity_values = entity[identifier]
            if not (entity_values.has_key("Unique") and 
                    entity_values["Unique"]):
                identifier = self.create_unique_identifier(identifier)
            entity_data = (entity_values["Entity"] 
                           if entity_values.has_key("Entity")
                           else {}
                           )
            if entity_values.has_key("Template"):
                self.update_from_template(entity_data,
                                          entity_values["Template"])
            self.get_or_create_entity(identifier, entity_data)

    def pump(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        ControllerBase.pump(self, time_delta)
        RPGWorld.pump(self, time_delta)
        self.current_map.update_entities(self)
        self.current_map.update_entitities_agent()
        
