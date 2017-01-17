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

"""This module contains the base application class.

.. module:: base
    :synopsis: Contains the base application class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import copy
import gettext
import imp
import os

from bGrease.grease_fife.mode import FifeManager
from fife import fife
from fife.extensions.basicapplication import ApplicationBase
from fife_rpg import Map
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.components.agent import Agent, STACK_POSITION
from fife_rpg.components.fifeagent import FifeAgent, setup_behaviour
from fife_rpg.components.general import General
from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg.systems import GameVariables
from fife_rpg.systems.scriptingsystem import ScriptingSystem
from fife_rpg.world import RPGWorld
import yaml
from xml.etree import cElementTree as etree

_SCRIPTING_MODULE = "application"


class KeyFilter(fife.IKeyFilter):

    """This is the implementation of the fife.IKeyFilter class.

    Prevents any filtered keys from being consumed by pychan.
    """

    def __init__(self, keys):
        """Sets up the keys to be filtered

        Args:
                keys: A list of fife.Key
        """
        fife.IKeyFilter.__init__(self)
        self._keys = keys

    def isFiltered(self, event):  # pylint: disable=W0221, C0103
        """Checks whether the key is filtered or not.

        Args:
            event: A fife.KeyEvent instance

        Returns:
            True if the key is filtered, False if not.
        """
        return event.getKey().getValue() in self._keys


class RPGApplication(FifeManager, ApplicationBase):

    """The main application.  It inherits fife.extensions.ApplicationBase.

    Properties:
        name: The name of the Application

        world: The fife_rpg.world.RPGWorld this application uses

        language: The language the application uses

        settings: A fife_settings.Setting instance that stores the settings of
        the application

        maps: A dictionary containing the maps the application has

        current_map: The current active map

        log_manager: The log manager of the application

        engine: A fife.Engine instance
    """

    def __init__(self, TDS):
        """Initialized the application

        Args:
            TDS: A fife_settings.Setting instance
        """
        ApplicationBase.__init__(self, TDS)
        FifeManager.__init__(self)
        self.name = self.settings.get("fife-rpg", "ProjectName")
        if self.name is None:
            raise AttributeError("The application name is not specified in"
                                 "the settings file")
        self._listener = None
        self.world = None
        self._maps = {}
        self._current_map = None
        self._languages = {}
        self._current_language = ""
        self._components = {}
        self._actions = {}
        self._systems = {}
        self._behaviours = {}
        self._map_switched_callbacks = []
        self._map_loaded_callbacks = []
        default_language = self.settings.get("i18n", "DefaultLanguage", "en")
        languages_dir = self.settings.get("i18n", "Directory", "__languages")
        for language in self.settings.get("i18n", "Languages", ("en",)):
            fallback = (language == default_language)
            self._languages[language] = gettext.translation(self.name,
                                                            languages_dir,
                                                            [language],
                                                            fallback=fallback)
        language = self.settings.get("i18n", "Language", default_language)
        self.switch_language(language)

    @property
    def language(self):
        """Returns the current set language"""
        return self._current_language

    @language.setter
    def language(self, language):
        """Sets the current language

        Args:
            language: The language to switch to
        """
        self.switch_language(language)

    @property
    def settings(self):
        """Returns the settings of the application.

        Returns:
            A fife_settings.Setting instance that contains the settings of the
            application.
        """
        return self._setting

    @property
    def log_manager(self):
        """Returns the log manager of the application.

        Returns:
            a fifelog.LogManager instance that contains the log manager of
            the application.
        """
        return self._log

    @property
    def current_map(self):
        """Returns the current active map"""
        return self._current_map

    @property
    def maps(self):
        """Returns a copy of the maps dictionary"""
        return copy(self._maps)

    @property
    def components(self):
        """Returns a copy of the available components"""
        return copy(self._components)

    @property
    def actions(self):
        """Returns a copy of the available actions"""
        return copy(self._actions)

    @property
    def systems(self):
        """Returns a copy of the available systems"""
        return copy(self._systems)

    @property
    def behaviours(self):
        """Returns a copy of the available behaviours"""
        return copy(self._behaviours)

    def switch_language(self, language):
        """Switch to the given language"""
        if language not in self._languages:
            raise KeyError("The language '%s' is not available" % language)
        if not language == self._current_language:
            self._languages[language].install()
            self._current_language = language

    def update_game_variables(self, variables):
        """Called by the game environment when it wants to update its globals

        Args:
            globals: The globals dictionary of the GameEnvironment that is
            filled by the GameScene
        """
        app_module = imp.new_module(_SCRIPTING_MODULE)
        app_module.__dict__["current_map"] = self.current_map
        app_module.__dict__["maps"] = self.maps
        variables[_SCRIPTING_MODULE] = app_module

    def add_map(self, identifier, game_map):
        """Adds a map to the maps dictionary.

        Args:
            identifier: The identifier of the map

            game_map: A Map instance.
        """
        if identifier not in self._maps:
            self._maps[identifier] = game_map
        else:
            raise AlreadyRegisteredError(identifier, "Map")

    def update_agents(self, game_map):
        """Updates the map to be in sync with the entities

        Args:
            game_map: The name of the map, or a Map instance
        """
        if isinstance(game_map, str):
            game_map = self.maps[game_map]
        if isinstance(game_map, str):  # The map is not yet loaded
            return
        object_namespace = self.settings.get("fife-rpg", "ObjectNamespace",
                                             "fife-rpg")
        fife_model = self.engine.getModel()
        game_map.update_entities()
        for entity in game_map.entities:
            agent = getattr(entity, Agent.registered_as)
            namespace = agent.namespace or object_namespace
            map_object = fife_model.getObject(agent.gfx,
                                              namespace.encode())
            if not map_object:
                raise RuntimeError("There is no object %s in the namespace %s"
                                   % (agent.gfx, namespace))
            general = getattr(entity, General.registered_as)
            layer = game_map.get_layer(agent.layer)
            fife_instance = layer.getInstance(general.identifier)
            if fife_instance:
                fife_object = fife_instance.getObject()
                if (fife_object.getId() != map_object.getId() or
                        fife_object.getNamespace() !=
                        map_object.getNamespace()):
                    layer.deleteInstance(fife_instance)
                    fife_instance = None
            if not fife_instance:
                position = agent.position
                fife_instance = layer.createInstance(
                    map_object,
                    fife.ExactModelCoordinate(position.x,
                                              position.y,
                                              position.z),
                    general.identifier)
                fife_instance.setRotation(agent.rotation)
                visual = fife.InstanceVisual.create(fife_instance)
                if map_object.getAction('default'):
                    target = fife.Location(game_map.actor_layer)
                    fife_instance.actRepeat('default', target)
                fifeagent = getattr(entity, FifeAgent.registered_as)
                behaviour_class = BehaviourManager.get_behaviour(
                    agent.behaviour_type)
                if behaviour_class is None:
                    raise RuntimeError("There is no registered behaviour %s"
                                       % agent.behaviour_type)
                behaviour = behaviour_class(**agent.behaviour_args)
                behaviour.agent = fife_instance
                fifeagent.behaviour = behaviour
                fifeagent.layer = layer
                fifeagent.instance = fife_instance
                setup_behaviour(fifeagent)
                fifeagent.behaviour.idle()
            else:
                visual = fife_instance.get2dGfxVisual()
            visual.setStackPosition(STACK_POSITION[agent.type])

    def map_loded(self, identifier):
        """Called from Map instances after the map was loaded

        Args:
            identifier: The identifier of the loaded map
        """
        if identifier in self._maps:
            game_map = self.maps[identifier]
            for callback in self._map_loaded_callbacks:
                callback(game_map)
            self.update_agents(game_map)

        else:
            raise LookupError("The map with the identifier '%s' cannot be "
                              "found"
                              % (identifier))

    def switch_map(self, name):
        """Switches to the given map.

        Args:
            name: The name of the map
        """
        old_map = None
        if self._current_map:
            old_map = self._current_map.name
            self._current_map.deactivate()
            self._current_map = None
        if name is None:
            for callback in self._map_switched_callbacks:
                callback(old_map, name)
            return
        if name in self._maps:
            self._current_map = self.maps[name]
            self._current_map.activate()
            for callback in self._map_switched_callbacks:
                callback(old_map, name)
        else:
            raise LookupError("The map with the name '%s' cannot be found"
                              % (name))

    def add_map_switch_callback(self, callback):
        """Adds a callback function which gets called after
        the map switched

        Args:
            callback: The function to add
        """
        if callback not in self._map_switched_callbacks:
            self._map_switched_callbacks.append(callback)

    def remove_map_switch_callback(self, callback):
        """Removes a callback function that got called after the map
        switched.

        Args:
            callback: The function to remove
        """
        if callback in self._map_switched_callbacks:
            index = self._map_switched_callbacks.index(callback)
            del self._map_switched_callbacks[index]

    def add_map_load_callback(self, callback):
        """Adds a callback function which gets called after
        a map was loaded

        Args:
            callback: The function to add
        """
        if callback not in self._map_loaded_callbacks:
            self._map_loaded_callbacks.append(callback)

    def remove_map_load_callback(self, callback):
        """Removes a callback function that got called after a map
        was loaded.

        Args:
            callback: The function to remove
        """
        if callback in self._map_loaded_callbacks:
            index = self._map_loaded_callbacks.index(callback)
            del self._map_loaded_callbacks[index]

    def load_maps(self):
        """Load the names of the available maps from a map file."""
        self._maps = {}
        maps_path = self.settings.get(
            "fife-rpg", "MapsPath", "maps")
        vfs = self.engine.getVFS()
        filename = os.path.join(maps_path, "maps.yaml")
        if not os.path.exists(filename):
            return
        maps_file = vfs.open(filename)
        maps_doc = yaml.load(maps_file)
        maps_path = self.settings.get(
            "fife-rpg", "MapsPath", "maps")
        camera = self.settings.get(
            "fife-rpg", "Camera", "main")

        for name, filename in maps_doc["Maps"].iteritems():
            filepath = os.path.join(maps_path, filename + '.xml')
            identifier = etree.parse(filepath).getroot().attrib["id"]
            regions_filename = ("%s_regions.yaml" %
                                os.path.splitext(filepath)[0])
            regions = {}
            try:
                regions_file = self.engine.getVFS().open(regions_filename)
            except fife.NotFound:
                regions_file = None
            if regions_file is not None:
                regions_data = yaml.load(regions_file)
                if regions_data is not None:
                    for region_name, region_data in (
                            regions_data.iteritems()):
                        region = fife.DoubleRect(x=region_data[0],
                                                 y=region_data[1],
                                                 width=region_data[2],
                                                 height=region_data[3])
                        regions[region_name] = region
            game_map = Map(filepath, name, camera, regions, self)
            self.add_map(identifier, game_map)

    def create_world(self):
        """Creates the world used by this application"""
        self.world = RPGWorld(self)
        GameVariables.add_callback(self.update_game_variables)
        ScriptingSystem.register_command("set_global_lighting",
                                         self.set_global_lighting,
                                         _SCRIPTING_MODULE)
        ScriptingSystem.register_command("get_global_lighting",
                                         self.get_global_lighting,
                                         _SCRIPTING_MODULE)
        ScriptingSystem.register_command("is_location_in_region",
                                         self.is_location_in_region,
                                         _SCRIPTING_MODULE)
        ScriptingSystem.register_command("is_agent_in_region",
                                         self.is_agent_in_region,
                                         _SCRIPTING_MODULE)

    def request_quit(self):
        """Sends the quit command to the application's listener.

        We could set self.quitRequested to true also but this is a
        good example on how to build and dispatch a fife.Command.
        """
        cmd = fife.Command()
        cmd.setSource(None)
        cmd.setCommandType(fife.CMD_QUIT_GAME)
        self.engine.getEventManager().dispatchCommand(cmd)

    def screen_coords_to_map_coords(self, click, layer):
        """Converts the screen coordinates to coordinates on the active map

        Args:

           click: Screen coordinates as fife.ScreenPoint or position tuple

           layer: The name of the layer the converted position should be on

        Returns: Converted coordinates as fife.Location
        """
        active_map = self.current_map
        if active_map is None:
            return None
        if not isinstance(click, fife.ScreenPoint):
            click = fife.ScreenPoint(click[0], click[1])
        coord = active_map.camera.toMapCoordinates(click, False)
        coord.z = 0
        location = fife.Location(active_map.get_layer(layer))
        location.setMapCoordinates(coord)
        return location

    def load_components(self, filename=None):
        """Load the component definitions from a file

        Args:
            filename: The path to the components file. If this is set to None
            the ComponentsFile or CombinedFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "ComponentsFile",
                                         "components.yaml")
            filename = self.settings.get("fife-rpg", "CombinedFile",
                                         filename)
        self._components = {}
        components_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(components_file)["Components"].iteritems():
            self._components[name] = path

    def get_component_data(self, component_name):
        """Returns the class and module of the given component

        Args:

            component_name: The name of the component
        """
        component_path = self._components[component_name]
        module = __import__(component_path, fromlist=[component_path])
        component = getattr(module, component_name)
        return component, module

    def register_component(self, component_name, registered_name=None,
                           register_checkers=True,
                           register_script_commands=True):
        """Calls the components register method.

        Args:
            component_name: Name of the component

            registered_name: Name under which the component should be
            registered

            register_checkers: If True a "register_checkers" function will be
            searched in the module and called

            register_script_commands: If True a "register_script_commands"
            functions will be searched in the module and called
        """
        component, module = self.get_component_data(component_name)
        if registered_name is not None:
            component.register(registered_name)
        else:
            component.register()
        if register_checkers and hasattr(module, "register_checkers"):
            module.register_checkers()
        if register_script_commands and hasattr(module,
                                                "register_script_commands"):
            module.register_script_commands(component.registered_as)

    def register_components(self, component_list=None, register_checkers=True,
                            register_script_commands=True):
        """Calls the register method of the components in the component list

        Args:
            component_list: A list of components if an item is not a string
            it will be interpreted as a tuple or list with the second item
            as the name to use when registering. If this is None the Components
            settings will be used.

            register_checkers: If True a "register_checkers" function will be
            search in the module and called

            register_script_commands: If True a "register_script_commands"
            functions will be searched in the module and called
        """
        if component_list is None:
            component_list = self.settings.get("fife-rpg", "Components")

        if component_list is None:
            raise ValueError("No component list supplied and no"
                             " \"Components\" Setting found")

        for component in component_list:
            if not isinstance(component, basestring):
                self.register_component(
                    *component,
                    register_checkers=register_checkers,
                    register_script_commands=register_script_commands)
            else:
                self.register_component(
                    component,
                    register_checkers=register_checkers,
                    register_script_commands=register_script_commands)

    def load_actions(self, filename=None):
        """Load the action definitions from a file

        Args:
            filename: The path to the actions file. If this is set to None the
            ActionsFile or CombinedFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "ActionsFile",
                                         "actions.yaml")
            filename = self.settings.get("fife-rpg", "CombinedFile",
                                         filename)
        self._actions = {}
        actions_file = self.engine.getVFS().open(filename)
        file_data = yaml.load(actions_file)
        for name, path in file_data["Actions"].iteritems():
            self._actions[name] = path

    def get_action_data(self, action_name):
        """Returns the class and module of the givenaction

        Args:

            action_name: The name of the action
        """
        action_path = self._actions[action_name]
        module = __import__(action_path, fromlist=[action_path])
        action = getattr(module, action_name)
        return action, module

    def register_action(self, action_name, registered_name=None):
        """Calls the actions register method.

        Args:
            action_name: Name of the action

            registered_name: Name under which the action should be registered
        """
        action = self.get_action_data(action_name)[0]
        if registered_name is not None:
            action.register(registered_name)
        else:
            action.register()

    def register_actions(self, action_list=None):
        """Calls the register method of the actions in the action list

        Args:
            action_list: A list of actions if an item is not a string
            it will be interpreted as a tuple or list with the second item
            as the name to use when registering. If this is None the Actions
            settings will be used.
        """
        if action_list is None:
            action_list = self.settings.get("fife-rpg", "Actions")

        if action_list is None:
            raise ValueError("No action list supplied and no \"Actions\" "
                             "Setting found")

        for action in action_list:
            if not isinstance(action, basestring):
                self.register_action(*action)
            else:
                self.register_action(action)

    def load_systems(self, filename=None):
        """Load the system definitions from a file

        Args:
            filename: The path to the systems file. If this is set to None the
            SystemsFile or CombinedFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "SystemsFile",
                                         "systems.yaml")
            filename = self.settings.get("fife-rpg", "CombinedFile",
                                         filename)
        self._systems = {}
        systems_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(systems_file)["Systems"].iteritems():
            self._systems[name] = path

    def get_system_data(self, system_name):
        """Returns the class and module of the given system

        Args:

            system_name: The name of the system
        """
        system_path = self._systems[system_name]
        module = __import__(system_path, fromlist=[system_path])
        system = getattr(module, system_name)
        return system, module

    def register_system(self, system_name, registered_name=None):
        """Calls the systems register method.

        Args:
            system_name: Name of the system

            registered_name: Name under which the system should be registered
        """
        system = self.get_system_data(system_name)[0]
        if registered_name is not None:
            system.register(registered_name)
        else:
            system.register()

    def register_systems(self, system_list=None):
        """Calls the register method of the systems in the system list

        Args:
            system_list: A list of systems if an item is not a string
            it will be interpreted as a tuple or list with the second item
            as the name to use when registering. If this is None the Systems
            settings will be used.
        """
        if system_list is None:
            system_list = self.settings.get("fife-rpg", "Systems")

        if system_list is None:
            raise ValueError("No system list supplied and no \"Systems\" "
                             "Setting found")

        for system in system_list:
            if not isinstance(system, basestring):
                self.register_system(*system)
            else:
                self.register_system(system)

    def load_behaviours(self, filename=None):
        """Load the behaviour definitions from a file

        Args:
            filename: The path to the behaviours file. If this is set to None
            the BehavioursFile or CombinedFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "BehavioursFile",
                                         "behaviours.yaml")
            filename = self.settings.get("fife-rpg", "CombinedFile",
                                         filename)
        self._behaviours = {}
        behaviours_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(behaviours_file)["Behaviours"].iteritems():
            self._behaviours[name] = path

    def get_behaviour_data(self, behaviour_name):
        """Returns the class and module of the given behaviour

        Args:

            behaviour_name: The name of the behaviour
        """
        behaviour_path = self._behaviours[behaviour_name]
        module = __import__(behaviour_path, fromlist=[behaviour_path])
        behaviour = getattr(module, behaviour_name)
        return behaviour, module

    def register_behaviour(self, behaviour_name, registered_name=None):
        """Calls the behaviours register method.

        Args:
            behaviour_name: Name of the behaviour

            registered_name: Name under which the behaviour should be
            registered
        """
        behaviour = self.get_behaviour_data(behaviour_name)[0]
        if registered_name is not None:
            behaviour.register(registered_name)
        else:
            behaviour.register()

    def register_behaviours(self, behaviour_list=None):
        """Calls the register method of the behaviours in the behaviour list

        Args:
            behaviour_list: A list of behaviours if an item is not a string
            it will be interpreted as a tuple or list with the second item
            as the name to use when registering. If this is None the Behaviours
            settings will be used.
        """
        if behaviour_list is None:
            behaviour_list = self.settings.get("fife-rpg", "Behaviours")

        if behaviour_list is None:
            raise ValueError("No behaviour list supplied and no"
                             " \"Behaviours\" Setting found")

        for behaviour in behaviour_list:
            if not isinstance(behaviour, basestring):
                self.register_behaviour(*behaviour)
            else:
                self.register_behaviour(behaviour)

    def load_combined(self, filepath=None):
        """Loads components, actions, systems and behaviours.

        Args:
            filepath: The path to the file. If set to None either the
            CominedFile Setting or the specific setting for the module will be
            used.
        """
        self.load_actions(filepath)
        self.load_behaviours(filepath)
        self.load_components(filepath)
        self.load_systems(filepath)

    def is_location_in_region(self, map_name, location, region_name):
        """Checks whether the location is in the region of the map

        Args:
            map_name: Name of the map. If None the current map will be used

            region_name: Name of the region

            location: A list or tuple containing the location
        """
        game_map = (self.maps[map_name]
                    if map_name is not None
                    else self.current_map)
        return game_map.is_in_region(location, region_name)

    def is_agent_in_region(self, map_name, agent_name, region_name):
        """Checks whether the agent is in the region of the map

        Args:
            map_name: Name of the map. If None the current map will be used

            region_name: Name of the region

            agent_name: Name of the agent
        """
        entity = self.world.get_entity(agent_name)
        agent = getattr(entity, Agent.registered_as)
        location = agent.position
        return self.is_location_in_region(map_name, location, region_name)

    def execute_console_command(self, command):
        """Executes a console command

        Args:
            command: The command string to execute

        Returns: The result of the command
        """
        return self._listener.onConsoleCommand(command)

    def check_agent_changes(self):
        """Checks all agents for changes"""
        extent = getattr(self.world[...], Agent.registered_as)
        extent = extent.map == self.current_map.name
        new_test = True
        for entity in extent:
            if not getattr(entity, FifeAgent.registered_as):
                new_test = False
        for agent, fifeagent in self.world.components.join(
                Agent.registered_as,
                FifeAgent.registered_as):
            map_test = agent.map == self.current_map.name

            fife_object = fifeagent.instance.getObject()
            gfx_test = (fife_object.getNamespace() == agent.namespace and
                        fife_object.getId() == agent.gfx)
            if map_test and gfx_test and new_test:
                continue
            agent.map = agent.new_map or agent.map
            agent.layer = agent.new_layer or agent.layer
            agent.position = agent.new_position or agent.position
            agent.rotation = agent.new_rotation or agent.rotation
            agent.new_map = None
            agent.new_layer = None
            agent.new_position = None
            agent.new_rotation = None

        self.update_agents(self.current_map)

    def set_global_lighting(self, red, green, blue):
        """Sets the color of the current maps lighting

        Args:
            red: The red value of the light as a float between 0.0 and 1.0

            green: The green value of the light as a float between 0.0 and 1.0

            blue: The blue value of the light as a float between 0.0 and 1.0
        """
        if self.current_map:
            self.current_map.camera.setLightingColor(red, green, blue)

    def get_global_lighting(self):
        """Returns the values of the current maps lighting"""
        if self.current_map:
            self.current_map.camera.getLightingColor()
        return (1.0, 1.0, 1.0)

    def step(self, time_delta):
        """Performs actions every frame.

        Args:
            time_delta: Time elapsed since last call to pump
        """
        if self.current_map:
            self.check_agent_changes()
            self.current_map.update_entities_fife()
            self.current_map.update_entities()
            self.current_map.update_entitities_agent()
        if self.world:
            self.world.step(time_delta)
        FifeManager.step(self, time_delta)


class BaseEventListener(fife.IKeyListener, fife.ICommandListener):

    """
    Default, rudimentary event listener.

    Will cause the application to quit on pressing ESC, or when a
    quit-game command was received.
    """

    def __init__(self, app):
        self.app = app
        self.engine = app.engine
        eventmanager = self.engine.getEventManager()
        # eventmanager.setNonConsumableKeys([fife.Key.ESCAPE])
        fife.IKeyListener.__init__(self)
        eventmanager.addKeyListener(self)
        fife.ICommandListener.__init__(self)
        eventmanager.addCommandListener(self)

    def keyPressed(self, evt):  # pylint: disable=W0221, C0103
        keyval = evt.getKey().getValue()
        if keyval == fife.Key.ESCAPE:
            self.app.quit()

    def keyReleased(self, evt):  # pylint: disable=W0221, C0103
        pass

    def onCommand(self, command):  # pylint: disable=W0221, C0103
        if command.getCommandType() == fife.CMD_QUIT_GAME:
            self.app.quit()
            command.consume()