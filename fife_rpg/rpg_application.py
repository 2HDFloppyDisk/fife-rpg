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
import sys
from StringIO import StringIO
import os
from copy import copy 
import gettext

import yaml
from bGrease.grease_fife.mode import FifeManager
from fife import fife
from fife.extensions.basicapplication import ApplicationBase
from fife.extensions.pychan.internal import get_manager

from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg import Map
from fife_rpg import code
from fife_rpg.world import RPGWorld
from fife_rpg.components.agent import Agent
from fife_rpg.components.fifeagent import FifeAgent, setup_behaviour
from fife_rpg.components.general import General
from fife_rpg.behaviours import BehaviourManager
from fife_rpg.systems import GameEnvironment

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
        elif cmd[0].lower() in ('eval'):
            try:
                result = str(eval(command.lstrip(cmd[0])))
            except: # pylint: disable-msg=W0702
                result = "Invalid eval statement..."
        else:
            result = self._application.onConsoleCommand(command)

        if not result: 
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
        self._listener = None
        self.world = None
        self.__maps = {}
        self.__current_map = None           
        self.__languages = {}
        self.__current_language = ""
        self.__components = {}
        self.__actions = {}
        self.__systems = {}
        default_language = self.settings.get("i18n", "DefaultLanguage", "")
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

    def update_environment(self, environment_globals):
        """Called by the game environment when it wants to update its globals
        
        Args:
            globals: The globals dictionary of the GameEnvironment that is 
            filled by the GameScene
        """
        environment_globals.update(self.maps)
        environment_globals["current_map"] = self.current_map
        environment_globals["_"] = _ #pylint: disable=E0602

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
            layer = getattr(game_map, "%s_layer" % agent.type)
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
                behaviour = behaviour_class(agent.walk_speed, agent.run_speed)
                behaviour.agent = fife_instance
                fifeagent.behaviour = behaviour
                fifeagent.layer = layer
                setup_behaviour(fifeagent)
                fifeagent.behaviour.idle()
            else:
                visual = fife_instance.get2dGfxVisual()
                location = fife_instance.getLocation()
                location.setExactLayerCoordinates(fife.ExactModelCoordinate(
                                                    *agent.position))
                fife_instance.setLocation(location)
            fife_instance.setRotation(agent.rotation)
            visual.setStackPosition(agent.stack_position)
            
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
                ground_layer = self.settings.get(
                "fife-rpg", "GroundLayer", "ground_layer")
                actor_layer = self.settings.get(
                "fife-rpg", "ActorLayer", "actors")
                ground_object_layer = self.settings.get(
                "fife-rpg", "GroundObjectLayer", "objects")
                item_layer = self.settings.get(
                "fife-rpg", "ItemLayer", "items")
                
                loader = fife.MapLoader(self.engine.getModel(), 
                                        self.engine.getVFS(), 
                                        self.engine.getImageManager(), 
                                        self.engine.getRenderBackend())
                
                filename = os.path.join(maps_path, game_map + '.xml')
                if loader.isLoadable(filename):               
                    fife_map = loader.load(filename)
                
                found_layer = False
                for layer in fife_map.getLayers():
                    if layer.getId() == item_layer:
                        found_layer = True
                        break                
                    
                if not found_layer:
                    fife_map.createLayer(item_layer, grid_type)

                found_layer = False
                for layer in fife_map.getLayers():
                    if layer.getId() == ground_object_layer:
                        found_layer = True
                        break                
                    
                if not found_layer:
                    fife_map.createLayer(ground_object_layer, grid_type)
                    
                found_layer = False
                for layer in fife_map.getLayers():
                    if layer.getId() == actor_layer:
                        found_layer = True
                        break                
                
                if not found_layer:
                    layer = fife_map.createLayer(actor_layer, grid_type)                    
                    layer.setWalkable(True)
                    layer.createCellCache()
                    layer.addInteractLayer(fife_map.getLayer(ground_layer))
                    cache = layer.getCellCache()
                    cache.createCells()
                    cache.forceUpdate()
                    
                regions_filename = "%s_regions.yaml" % os.path.splitext(filename)[0]
                regions = {}
                regions_file = file(regions_filename, "r")
                regions_data = yaml.load(regions_file)
                for region_name,  region_data in regions_data.iteritems():
                    region = fife.DoubleRect(x=region_data[0],
                                             y=region_data[1],
                                             width=region_data[2],
                                             height=region_data[3])
                    regions[region_name] = region
                game_map = Map(fife_map, name, camera, actor_layer,            
                               ground_object_layer, item_layer, regions)
                renderer = fife.InstanceRenderer.getInstance(game_map.camera)
                renderer.addActiveLayer(game_map.item_layer)
                renderer.addActiveLayer(game_map.ground_object_layer)
                renderer.addActiveLayer(game_map.actor_layer)
                
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
        maps_path = self.settings.get(
            "fife-rpg", "MapsPath", "maps")
        vfs = self.engine.getVFS()
        maps_file = vfs.open(os.path.join(maps_path, "maps.yaml"))
        maps_doc = yaml.load(maps_file)
        for name, filename in maps_doc["Maps"].iteritems():
            self.add_map(name, filename)
            
    def move_agent(self, entity, position=None, rotation=None, 
                   stack_position=None, new_map=None):
        """Instantly moves an agent on the current map, or to a new map
        
        Args:
            entity: The entity of the agent to move or the name of the agent
            
            position: The new position of the agent
            
            rotation: The new rotation of the agent
            
            stack_postition: The new stack position of the agent
            
            new_map: The new map to move the agent to.
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if isinstance(position, fife.Location):
            model_coordinates = position.getExactLayerCoordinates()
            position=(model_coordinates.x, model_coordinates.y)
        fifeagent = getattr(entity, FifeAgent.registered_as)
        if not fifeagent:
            print "The entity is not a fife agent"
            return
        agent = getattr(entity, Agent.registered_as)
        current_map = agent.map
        if new_map and new_map != current_map:
            current_game_map = self.maps[current_map]
            current_game_map.remove_entity(entity.identifier)
            agent.map = new_map
            new_game_map = self.maps[new_map]
            if not isinstance(new_game_map, str):
                new_game_map.update_entities(self.world)
            self.update_agents(current_game_map)
        agent.position = position or agent.position
        agent.rotation = rotation or agent.rotation
        agent.stack_position = stack_position or agent.stack_position        
        self.update_agents(agent.map)
            
    def createListener(self):# pylint: disable-msg=C0103
        """Creates the listener for the application and returns it."""
        self._listener = ApplicationListener(self.engine,  self)
        return self._listener

    def create_world(self):
        """Creates the world used by this application"""
        self.world = RPGWorld(self)
        registered_as = GameEnvironment.registered_as            
        if registered_as and hasattr(self.world.systems, registered_as):
            environment = getattr(self.world.systems, registered_as) 
            environment.add_callback(self.update_environment)

    def request_quit(self):
        """Sends the quit command to the application's listener.

        We could set self.quitRequested to true also but this is a
        good example on how to build and dispatch a fife.Command.
        """
        cmd = fife.Command()
        cmd.setSource(None)
        cmd.setCommandType(fife.CMD_QUIT_GAME)
        self.engine.getEventManager().dispatchCommand(cmd)


    def handle_python(self, command):
        """Handles python commands
        
        Args:
            command: The command string
            
            env_locals: The locals that will be used
            
            env_globals: The globals that will be used
        
        Returns:
            The result of the command
        """
        current_mode = self.current_mode
        if current_mode and isinstance(current_mode, RPGWorld):
            environment = getattr(current_mode.systems, 
                                  GameEnvironment.registered_as)
            env_locals, env_globals = environment.get_environement()       

            env_globals.update({"__name__":"__rpg_console__", "__doc__":None})
            console = code.InteractiveConsole(env_globals, env_locals)
            codeOut = StringIO()
            #make stdout and stderr write to our file, not the terminal
            sys.stdout = codeOut
            sys.stderr = codeOut
            #Process the code
            try:
                console.push(command)
            except Exception as error: #pylint: disable=W0703
                print error
            output = codeOut.getvalue()
            #restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            temp_output = output
            output = ""
            counter = 0
            #Make the output fit in the console screen
            for char in temp_output:
                counter += 1
                if char == "\n":
                    counter = 0
                elif counter == 110:
                    output += "\n"
                    counter = 0
                output += char
            
            return output
        return ""

    def onConsoleCommand(self, command):# pylint: disable-msg=C0103,W0221
        """Process console commands

        Args:
            command: A string containing the command

        Returns:
            A string representing the result of the command
        """
        result = ""
        if GameEnvironment.registered_as:
            
            if (command.startswith("python")):
                return self.handle_python(command[7:])
            else:
                return self.handle_python(command)
    
        return result
        
    def pump(self, dt):
        """Performs actions every frame.        
        
        Args:
            dt: Time elapsed since last call to pump
        """
        if self._listener.quit:
            self.quit()
        self.current_map.update_entities(self.world)
        self.current_map.update_entitities_agent()
        if self.world:
            self.world.pump(dt)
        FifeManager.pump(self, dt)
    
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
        components_file = file(filename, "r")
        for name, path in yaml.load(components_file).iteritems():
            self.__components[name] = path 
        components_file.close()
        
    def register_component(self, component_name, registered_name=None,
                           register_checkers=True):
        """Calls the components register method.
        
        Args:
            component_name: Name of the component
            
            registered_name: Name under which the component should be registered
            
            register_checkers: If True a "register_checkers" function will be search
            in the module and called
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

    def register_components(self, component_list=None, register_checkers=True):
        """Calls the register method of the components in the component list
        
        Args:
            component_list: A list of components if an item is not a string
            it will be interpreted as a tuple or list with the second item
            as the name to use when registering. If this is None the Components
            settings will be used.
            
            register_checkers: If True a "register_checkers" function will be search
            in the module and called
        """
        if component_list is None:
            component_list = self.settings.get("fife-rpg", "Components")
        
        if component_list is None:
            raise ValueError("No component list supplied and no \"Components\" "
                             "Setting found")
           
        for component in component_list:
            if not isinstance(component, str):
                self.register_component(*component, 
                                        register_checkers=register_checkers)
            else:
                self.register_component(component, 
                                        register_checkers=register_checkers)
                
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
        actions_file = file(filename, "r")
        for name, path in yaml.load(actions_file).iteritems():
            self.__actions[name] = path 
        actions_file.close()
        
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
        systems_file = file(filename, "r")
        for name, path in yaml.load(systems_file).iteritems():
            self.__systems[name] = path 
        systems_file.close()
        
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