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

#  This module is based on the scriptingsystem module from PARPG

"""The scripting system manages the scripts of fife-rpg games.

.. module:: scriptingsystem
    :synopsis: Manages the scripts of fife-rpg games.
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from collections import deque
from copy import copy

import yaml

from fife_rpg.systems import Base
from fife_rpg.systems import GameVariables
from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg.helpers import ClassProperty


class Script(object):
    """Script object
    
    Properties:
        actions: The actions that the script will run
        
        system: The ScriptingSystem that this script will run on
        
        running_actions: The actions that are currently running
        
        running: Whether the script is currently running or not
        
        finished: Whether the script has finished running or not
        
        wait: The seconds that have to pass before the next action is run.
        
        cur_action: The current running action     
    """

    def __init__(self, actions, system):
        assert(isinstance(actions, deque))
        self.actions = actions
        assert(isinstance(system, ScriptingSystem))
        self.system = system
        self.running_actions = None
        self.running = False
        self.finished = False
        self._time = 0
        self.wait = 0
        self.cur_action = None
        self.reset()

    def reset(self):
        """Resets the state of the script"""
        self.running_actions = copy(self.actions)
        self.running = False
        self.finished = False
        self._time = 0
        self.wait = 0
        self.cur_action = None
    
    def update(self, time):
        """Advance the script
        
        Args:
            time: The time to advance the script by
        """
        if not self.running:
            return
        if self.cur_action and not self.cur_action.executed:
            return
        self._time += time
        if self.wait <= self._time:
            self._time = 0
            try:
                arg_types = {}
                arg_types["Entity"] = self.system.world.get_entity
                registered_as = GameVariables.registered_as
                if registered_as:
                    environment = getattr(self.system.world.systems,
                                          registered_as)
                    arg_types["Variable"] = environment.get_variable
                action_data = self.running_actions.popleft()
                action = self.system.actions[action_data["Action"]]
                action_type = (action_data["Type"] if action_data.has_key("Type")
                                else "")
                if action_type == "Entity":
                    agent = self.system.world.get_entity(action_data["Agent"])
                    target = self.system.world.get_entity(action_data["Target"])
                    action_commands = (action_data["ActionCommands"] if
                                       action_data.has_key("ActionCommands") else
                                       {}
                                       )
                        
                    self.cur_action = action(self.system.world.application,
                                             agent, target, action_commands)
                else:
                    kwargs = {}
                    for arg, data in action_data["Args"].iteritems():
                        if data.has_key("Type"):
                            arg_type = data["Type"]
                            kwargs[arg] = arg_types[arg_type](data["Value"])
                        else:
                            kwargs[arg] = data["Value"]
                    kwargs["commands"] = (action_data["ActionCommands"] if
                                       action_data.has_key("ActionCommands") else
                                       {}
                                       )
                        
                    self.cur_action = action(self.system.world.application,
                                             **kwargs)
                                        
                self.wait = action_data["Time"]
                if action_data.has_key("Command"):
                    vals = []
                    
                    for val in action_data["Command"]["Variables"]:
                        if val.has_key("Type"):
                            val_type = val["Type"]
                            value = arg_types[val_type](val["Value"])
                        else:
                            value = val["Value"]
                        vals.append(value)
                    command = action_data["Command"]["Name"]
                    self.system.commands[command](
                        *vals, 
                        callback=self.cur_action.execute
                        )
                else:
                    self.cur_action.execute()
            except IndexError:
                self.finished = True
                self.running = False


class ScriptingSystem(Base):
    """System responsible for managing scripts.
    
    Properties:
        actions: Actions that the scripts can do
        
        scripts: Dictionary of the registered scripts
        
        conditions: List of the registered conditions
    """

    dependencies = []
    
    __condition_dictionary = {}
    __commands = {}
    
    @classmethod
    def register(cls, name="scripting"):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered
            
        Returns:
            True if the system was registered, False if not.
        """
        return (super(ScriptingSystem, cls).register(name))
    
    @classmethod
    def register_condition(cls, name, condition_function):
        """Register a condition to the condition dictionary.
        
        Args:
            name: The name of the condition
            condition_function: The condition function. This should be a
            function that returns True or False
        """
        if name in cls.__condition_dictionary:
            raise AlreadyRegisteredError(name, "Condition")
        cls.__condition_dictionary[name] = condition_function
        
    @ClassProperty
    @classmethod
    def condition_dictionary(cls):
        return copy(cls.__condition_dictionary)

    @classmethod
    def register_command(cls, name, command_function):
        """Register a command to the command dictionary.
        
        Args:
            name: The name of the command
            command_function: The command function.
        """
        if name in cls.__commands:
            raise AlreadyRegisteredError(name, "command")
        cls.__commands[name] = command_function

    @classmethod
    def register_commands(cls, command_dict):
        """Register a command to the command dictionary.
        
        Args:
            command_dict: A dictionary with commands.
        """
        for name, command_function in command_dict.iter_items():
            cls.register_command(name, command_function)
        
    @ClassProperty
    @classmethod
    def commands(cls):
        return copy(cls.__commands)
    
    def __init__(self):
        Base.__init__(self)
        self.actions = {}
        self.scripts = {}
        self.conditions = []
        self.reset()

    def reset(self):
        """Resets the script and condition collections"""
        self.scripts = {}
        self.conditions = []

    @classmethod
    def check_condition(cls, application, expressions):
        """Iterates over the expressions of the condition and returns
        whether all evaluate to True or not.
        
        Args:
            application: A :class:`fife_rpg.rpg_application.RPGApplication`
            object
            
            expressions: A list of expressions
            
        Returns:
            True: If ALL expressions evaluate to True
            
            False: If one of the expressions evaluates to False
        """
        for expression in expressions:
            name = expression["Type"]
            args = expression["Args"]
            reverse = False
            if name.startswith("Not_"):
                name = name[4:]
                reverse = True
            condition_function = cls.__condition_dictionary[name]
            if not reverse:
                result = not condition_function(application, *args)
            else:
                result = condition_function(application, *args)
            if result:
                return False
                
        return True

    def step(self, time_delta):
        """Execute a _time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time since last step invocation
        """
        for condition_data in self.conditions:
            script_name = condition_data["Script"]
            if not self.scripts.has_key(script_name):
                return
            script = self.scripts[script_name]
            expressions = condition_data["Expressions"]
            script.running = self.check_condition(self.world.application,
                                                  expressions)
        for script in self.scripts.itervalues():
            assert(isinstance(script, Script))
            if script.finished:
                script.reset()
            elif script.running:
                script.update(time_delta)
                
    def set_script(self, name, actions):
        """Sets a script.

        Args:
            name: The name of the script
            
            actions: What the script does
        """
        if not(isinstance(actions, deque)):
            actions = deque(actions)
        self.scripts[name] = Script(actions, 
                                    self
                                    )
        
    def add_condition(self, condition_data):
        """Adds a condition.

        Args:
            condition_data: Dictionary containing the data of the condition
        """
        self.conditions.append(condition_data)
    
    
    def run_script(self, name):
        """Runs a script with the given name

        Args:
            name: The name of the script
        """
        if self.scripts.has_key(name):
            self.scripts[name].running = True
        
    def load_scripts(self, filename=None):
        """Load scripts from a file
        
        Args:
            filename: The path to the scripts file. If set to None the 
            "ScriptsFile" setting will be used.
        """
        application = self.world.application
        if filename is None:
            filename = application.settings.get("fife-rpg", "ScriptsFile",
                                                "scripts.yaml")
        scripts_file = application.engine.getVFS().open(filename)
        scripts_data = yaml.load(scripts_file)
        scripts = (scripts_data["Scripts"])
        conditions = (
            scripts_data["Conditions"] if 
            scripts_data.has_key("Conditions") else ()
        )
        if scripts is not None:
            for name, actions in scripts.iteritems():
                self.set_script(name, actions)
        if conditions is not None:
            for condition in conditions:
                self.add_condition(condition)           
        
