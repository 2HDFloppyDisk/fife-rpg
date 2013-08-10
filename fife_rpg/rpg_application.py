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

"""This module contains the main application class.

.. module:: rpg_application
    :synopsis: Contains the main application class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import time
import os
from copy import copy 
import gettext
import imp

import yaml
from bGrease.grease_fife.mode import FifeManager
from fife import fife
from fife.extensions.basicapplication import ApplicationBase
from fife.extensions.pychan.internal import get_manager

from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg import Map
from fife_rpg.world import RPGWorld
from fife_rpg.components.agent import Agent, STACK_POSITION
from fife_rpg.components.fifeagent import FifeAgent, setup_behaviour
from fife_rpg.components.general import General
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.systems import GameVariables
from fife_rpg.systems.scriptingsystem import ScriptingSystem
from fife_rpg.console_commands import get_commands

_scripting_module = "application"

class KeyFilter(fife.IKeyFilter):
    """This is the implementation of the fife.IKeyFilter class.

    Prevents any filtered keys from being consumed by guichan.
    """

    def __init__(self, keys):
        """Sets up the keys to be filtered

        Args:
                keys: A list of fife.Key
        """
        fife.IKeyFilter.__init__(self)
        self._keys = keys
    
    def isFiltered(self, event): # pylint: disable-msg=W0221
        """Checks whether the key is filtered or not.

        Args:
            event: A fife.KeyEvent instance

        Returns:
            True if the key is filtered, False if not.
        """
        return event.getKey().getValue() in self._keys


class ApplicationListener(
    fife.IKeyListener, fife.ICommandListener, fife.ConsoleExecuter):
    """A basic listener for window commands, console commands and keyboard
    inputs.

    Does not process game related input.
    
    Properties:
        quit: Sets whether to quit the application on the next pump or not.
    """

    def __init__(self, engine, application):
        """Initializes all listeners and registers itself with the
        eventmanager.

        Args:
            engine: A fife.Engine instance
            
            application: A RPGApplication instance
        """
        self._engine = engine
        self._application = application
        self._eventmanager = self._engine.getEventManager()

        fife.IKeyListener.__init__(self)
        self._eventmanager.addKeyListener(self)

        fife.ICommandListener.__init__(self)
        self._eventmanager.addCommandListener(self)

        fife.ConsoleExecuter.__init__(self)
        get_manager().getConsole().setConsoleExecuter(self)

        keyfilter = KeyFilter([fife.Key.ESCAPE, fife.Key.CARET,
                               fife.Key.PRINT_SCREEN])
        keyfilter.__disown__()

        self._eventmanager.setKeyFilter(keyfilter)

        self.quit = False

    def keyPressed(self, event):# pylint: disable-msg=C0103,W0221
        """Processes any non game related keyboard input.

        Args:
            event: The fife.KeyEvent that happened
        """
        if event.isConsumed():
            return

        keyval = event.getKey().getValue()
                
        if keyval == fife.Key.ESCAPE:
            self.quit = True
            event.consume()
        elif keyval == fife.Key.CARET:
            get_manager().getConsole().toggleShowHide()
            event.consume()
        elif keyval == fife.Key.PRINT_SCREEN:
            self._engine.getRenderBackend().captureScreen(
                time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".png")
            event.consume()

    def keyReleased(self, event):# pylint: disable-msg=C0103,W0221
        """Gets called when a key is released

        Args:
            event: The fife.KeyEvent that happened
        """
        pass

    def onCommand(self, command):# pylint: disable-msg=C0103,W0221
        """Process commands

        Args:
            command: The fife.Command that is being processed
        """
        self.quit = (command.getCommandType() == fife.CMD_QUIT_GAME)
        if self.quit:
            command.consume()

    def onConsoleCommand(self, command):# pylint: disable-msg=C0103,W0221
        """Process console commands

        Args:
            command: A string containing the command

        Returns:
            A string representing the result of the command
        """
        result = ""

        args = command.split(" ")
        cmd = []
        for arg in args:
            arg = arg.strip()
            if arg != "":
                cmd.append(arg)

        if cmd[0].lower() in ('quit', 'exit'):
            self.quit = True
            result = 'quitting'
        elif cmd[0].lower() in ('help'):
            helptextfile = self._application.settings.get(
                "RPG", "HelpText", "misc/help.txt")
            get_manager().getConsole().println(open(helptextfile, 'r').read())
            result = "--OK--"
        elif cmd[0] in get_commands():
            result = get_commands()[cmd[0]](self._application, *cmd[1:])
        else:
            result = 'Command Not Found...'

        return result

    def onToolsClick(self):# pylint: disable-msg=C0103,W0221
        """Gets called when the the 'tool' button on the console is clicked"""
        print "No tools set up yet"


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
        self.__maps = {}
        self.__current_map = None           
        self.__languages = {}
        self.__current_language = ""
        self.__components = {}
        self.__actions = {}
        self.__systems = {}
        self.__behaviours = {}
        self.__map_switched_callbacks = []
        default_language = self.settings.get("i18n", "DefaultLanguage", "en")
        languages_dir = self.settings.get("i18n", "Directory", "__languages")
        for language in self.settings.get("i18n", "Languages", ("en", )):
            fallback = (language == default_language)
            self.__languages[language] = gettext.translation(self.name, 
                                                            languages_dir,
                                                            [language],
                                                            fallback=fallback)
        language = self.settings.get("i18n", "Language", default_language)
        self.switch_language(language)
    
    @property
    def language(self):
        """Returns the current set language"""
        return self.__current_language
    
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
        return self.__current_map

    @property
    def maps(self):
        """Returns a copy of the maps dictionary"""
        return copy(self.__maps)

    def switch_language(self, language):
        """Switch to the given language"""
        if not self.__languages.has_key(language):
            raise KeyError("The language '%s' is not available" % language)
        if not language == self.__current_language:
            self.__languages[language].install()
            self.__current_language = language

    def update_game_variables(self, variables):
        """Called by the game environment when it wants to update its globals
        
        Args:
            globals: The globals dictionary of the GameEnvironment that is 
            filled by the GameScene
        """
        app_module = imp.new_module(_scripting_module)
        app_module.__dict__["current_map"] = self.current_map
        app_module.__dict__["maps"] = self.maps
        variables[_scripting_module] = app_module

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

    def update_agents(self, game_map):
        """Updates the map to be in sync with the entities
        
        Args:
            game_map: The name of the map, or a Map instance
        """
        if isinstance(game_map, str):
            game_map = self.maps[game_map]
        if isinstance(game_map, str): #The map is not yet loaded
            return
        object_namespace = self.settings.get("fife-rpg", "ObjectNamespace", 
                                             "fife-rpg")
        fife_model = self.engine.getModel()
        for entity in game_map.entities:
            agent = getattr(entity, Agent.registered_as)
            map_object = fife_model.getObject(agent.gfx, 
                object_namespace)
            general = getattr(entity, General.registered_as)
            layer = game_map.get_layer(agent.layer)
            fife_instance = layer.getInstance(general.identifier)
            if not fife_instance:                 
                fife_instance = layer.createInstance(
                    map_object, 
                    fife.ExactModelCoordinate(*agent.position), 
                    general.identifier)
                visual = fife.InstanceVisual.create(fife_instance)
                if (map_object.getAction('default')):
                    target = fife.Location(game_map.actor_layer)
                    fife_instance.act('default', target, True)
                fifeagent = getattr(entity, FifeAgent.registered_as)
                behaviour_class = BehaviourManager.get_behaviour(
                                                        agent.behaviour_type)
                behaviour = behaviour_class(**agent.behaviour_args)
                behaviour.agent = fife_instance
                fifeagent.behaviour = behaviour
                fifeagent.layer = layer
                fifeagent.instance = fife_instance
                setup_behaviour(fifeagent)
                fifeagent.behaviour.idle()
            else:
                visual = fife_instance.get2dGfxVisual()
                location = fife_instance.getLocation()
                location.setExactLayerCoordinates(fife.ExactModelCoordinate(
                                                    *agent.position))
                fife_instance.setLocation(location)
            fife_instance.setRotation(agent.rotation)
            visual.setStackPosition(STACK_POSITION[agent.type])
            
    def load_map(self, name):
        """Load the map with the given name

        Args:
            name: The name of the map to load
        """
        if name in self.__maps:
            game_map = self.__maps[name]
            if not isinstance(game_map, Map):
                maps_path = self.settings.get(
                    "fife-rpg", "MapsPath", "maps")
                grid_type = self.settings.get(
                    "fife-rpg", "GridType", "square")
                grid_type = (self.engine.getModel().
                                getCellGrid(grid_type)
                             )
                camera = self.settings.get(
                    "fife-rpg", "Camera", "main")
                
                loader = fife.MapLoader(self.engine.getModel(), 
                                        self.engine.getVFS(), 
                                        self.engine.getImageManager(), 
                                        self.engine.getRenderBackend())
                
                filename = os.path.join(maps_path, game_map + '.xml')
                if loader.isLoadable(filename):               
                    fife_map = loader.load(filename)               
                    
                regions_filename = ("%s_regions.yaml" % 
                                    os.path.splitext(filename)[0])
                regions = {}
                try:
                    regions_file = self.engine.getVFS().open(regions_filename)
                except RuntimeError:
                    regions_file = None
                if regions_file is not None:
                    regions_data = yaml.load(regions_file)
                    if regions_data is not None:
                        for region_name, region_data in regions_data.iteritems():
                            region = fife.DoubleRect(x=region_data[0],
                                                     y=region_data[1],
                                                     width=region_data[2],
                                                     height=region_data[3])
                            regions[region_name] = region
                game_map = Map(fife_map, name, camera, regions)
                
                game_map.update_entities(self.world)
                self.__maps[name] = game_map
            self.update_agents(game_map)

        else:
            raise LookupError("The map with the name '%s' cannot be found"
                              %(name))
                
    def switch_map(self, name):
        """Switches to the given map.

        Args:
            name: The name of the map
        """
        if self.__current_map:
            self.__current_map.deactivate()
            self.__current_map = None
        if name is None:
            return
        if name in self.__maps:
            self.load_map(name)
            self.__current_map = self.maps[name]
            self.__current_map.activate()
            for callback in self.__map_switched_callbacks:
                callback()
        else:
            raise LookupError("The map with the name '%s' cannot be found" 
                        %(name))
    
    def add_map_switch_callback(self, callback):
        """Adds a callback function which gets called after 
        the map switched
        
        Args:
            callback: The function to add
        """
        if callback not in self.__map_switched_callbacks:
            self.__map_switched_callbacks.append(callback)

    def remove_map_switch_callback(self, callback):
        """Removes a callback function that got called after the map
        switched.
        
        Args:
            callback: The function to remove
        """
        if callback in self.__map_switched_callbacks:
            index = self.__map_switched_callbacks.index(callback)
            del self.__map_switched_callbacks[index]
        
    def load_maps(self):
        """Load the names of the available maps from a map file."""
        self.__maps = {}
        maps_path = self.settings.get(
            "fife-rpg", "MapsPath", "maps")
        vfs = self.engine.getVFS()
        maps_file = vfs.open(os.path.join(maps_path, "maps.yaml"))
        maps_doc = yaml.load(maps_file)
        for name, filename in maps_doc["Maps"].iteritems():
            self.add_map(name, filename)            
           
    def createListener(self):# pylint: disable-msg=C0103
        """Creates the listener for the application and returns it."""
        self._listener = ApplicationListener(self.engine,  self)
        return self._listener

    def create_world(self):
        """Creates the world used by this application"""
        self.world = RPGWorld(self)
        GameVariables.add_callback(self.update_game_variables)

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
            filename: The path to the components file. If this is set to None the
            ComponentsFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "ComponentsFile", 
                                         "components.yaml")
        self.__components = {}        
        components_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(components_file)["Components"].iteritems():
            self.__components[name] = path 
        
    def register_component(self, component_name, registered_name=None,
                           register_checkers=True, 
                           register_script_commands=True):
        """Calls the components register method.
        
        Args:
            component_name: Name of the component
            
            registered_name: Name under which the component should be registered
            
            register_checkers: If True a "register_checkers" function will be searched
            in the module and called
            
            register_script_commands: If True a "register_script_commands" functions
            will be searched in the module and called
        """
        component_path = self.__components[component_name]
        module = __import__(component_path, fromlist=[component_path])
        component = getattr(module, component_name)
        if not registered_name is None:
            component.register(registered_name)
        else:
            component.register()
        if register_checkers and hasattr(module, "register_checkers"):
            module.register_checkers()
        if register_script_commands and hasattr(module, "register_script_commands"):
            module.register_script_commands(component.registered_as)

    def register_components(self, component_list=None, register_checkers=True,
                            register_script_commands=True):
        """Calls the register method of the components in the component list
        
        Args:
            component_list: A list of components if an item is not a string
            it will be interpreted as a tuple or list with the second item
            as the name to use when registering. If this is None the Components
            settings will be used.
            
            register_checkers: If True a "register_checkers" function will be search
            in the module and called
            
            register_script_commands: If True a "register_script_commands" functions
            will be searched in the module and called            
        """
        if component_list is None:
            component_list = self.settings.get("fife-rpg", "Components")
        
        if component_list is None:
            raise ValueError("No component list supplied and no \"Components\" "
                             "Setting found")
           
        for component in component_list:
            if not isinstance(component, str):
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
            ActionsFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "ActionsFile", 
                                         "actions.yaml")
        self.__actions = {}        
        actions_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(actions_file)["Actions"].iteritems():
            self.__actions[name] = path 
        
    def register_action(self, action_name, registered_name=None):
        """Calls the actions register method.
        
        Args:
            action_name: Name of the action
            
            registered_name: Name under which the action should be registered            
        """
        action_path = self.__actions[action_name]
        module = __import__(action_path, fromlist=[action_path])
        action = getattr(module, action_name)
        if not registered_name is None:
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
            if not isinstance(action, str):
                self.register_action(*action)
            else:
                self.register_action(action)
                
    def load_systems(self, filename=None):
        """Load the system definitions from a file
        
        Args:
            filename: The path to the systems file. If this is set to None the
            SystemsFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "SystemsFile", 
                                         "systems.yaml")
        self.__systems = {}        
        systems_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(systems_file)["Systems"].iteritems():
            self.__systems[name] = path 
        
    def register_system(self, system_name, registered_name=None):
        """Calls the systems register method.
        
        Args:
            system_name: Name of the system
            
            registered_name: Name under which the system should be registered            
        """
        system_path = self.__systems[system_name]
        module = __import__(system_path, fromlist=[system_path])
        system = getattr(module, system_name)
        if not registered_name is None:
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
            if not isinstance(system, str):
                self.register_system(*system)
            else:
                self.register_system(system)

    def load_behaviours(self, filename=None):
        """Load the behaviour definitions from a file
        
        Args:
            filename: The path to the behaviours file. If this is set to None the
            BehavioursFile setting will be used.
        """
        if filename is None:
            filename = self.settings.get("fife-rpg", "BehavioursFile", 
                                         "behaviours.yaml")
        self.__behaviours = {}        
        behaviours_file = self.engine.getVFS().open(filename)
        for name, path in yaml.load(behaviours_file)["Behaviours"].iteritems():
            self.__behaviours[name] = path 

    def register_behaviour(self, behaviour_name, registered_name=None):
        """Calls the behaviours register method.
        
        Args:
            behaviour_name: Name of the behaviour
            
            registered_name: Name under which the behaviour should be registered            
        """
        behaviour_path = self.__behaviours[behaviour_name]
        module = __import__(behaviour_path, fromlist=[behaviour_path])
        behaviour = getattr(module, behaviour_name)
        if not registered_name is None:
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
            raise ValueError("No behaviour list supplied and no \"Behaviours\" "
                             "Setting found")
           
        for behaviour in behaviour_list:
            if not isinstance(behaviour, str):
                self.register_behaviour(*behaviour)
            else:
                self.register_behaviour(behaviour)

    def is_location_in_region(self, map_name, location, region_name):
        """Checks whether the location is in the region of the map
        
        Args:
            map_name: Name of the map. If None the current map will be used
            
            region_name: Name of the region
            
            location: A list or tuple containing the location
        """
        game_map = (self.maps[map_name] 
                    if not map_name is None 
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
        for agent in self.world.components.join(Agent.registered_as):
            agent = agent[0]
            if agent.map == self.current_map.name:
                continue
            agent.map = agent.new_map or agent.map
            agent.layer = agent.new_layer or agent.layer
            agent.position = agent.new_position or agent.position
            agent.rotation = agent.new_rotation or agent.rotation
            agent.new_map = None
            agent.new_layer = None
            agent.new_position = None
            agent.new_rotation = None
            if agent.map:
                if self.maps.has_key(agent.map):
                    game_map = self.maps[agent.map]
                    if not isinstance(game_map, str):
                        game_map.update_entities(self.world)
                        self.update_agents(game_map)
                else:
                    raise KeyError("Tried to access map `%s`, which does not exist" % (agent.map))
                    
    def pump(self, dt):
        """Performs actions every frame.        
        
        Args:
            dt: Time elapsed since last call to pump
        """
        if self._listener.quit:
            self.quit()
        if self.current_map:
            self.check_agent_changes()
            self.current_map.update_entities_fife()
            self.current_map.update_entities(self.world)
            self.current_map.update_entitities_agent()
        if self.world:
            self.world.pump(dt)
        FifeManager.pump(self, dt)
    
#Register conditions
ScriptingSystem.register_command("is_location_in_region", 
                                   RPGApplication.is_location_in_region,
                                   _scripting_module)
ScriptingSystem.register_command("is_agent_in_region", 
                                   RPGApplication.is_agent_in_region,
                                   _scripting_module)

