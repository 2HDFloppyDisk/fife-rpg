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

from copy import copy

import yaml

from fife_rpg.systems import Base
from fife_rpg.systems import GameVariables
from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg.helpers import ClassProperty
import imp

class ScriptingSystem(Base):
    """System responsible for managing scripts.

    Properties:

        globals: The globals available to scripts

        __scripts: Dictionary of the registered scripts

    """

    dependencies = []

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
        self.reset()

    def reset(self):
        """Resets the scripting system"""
        self.globals = {}
        self.__scripts = []
    
    def prepare_globsl(self):
        """Builds the actual globals passed to scripts and returns them
        as a dictionary"""
        script_globals = {}
        if GameVariables.registered_as:
            game_variables = getattr(self.world.systems,
                                     GameVariables.registered_as)
            script_globals.update(game_variables.get_variables())
        script_globals.update(self.globals)
        script_globals.update(self.commands)
        return script_globals
    
    def step(self, time_delta):
        """Execute a time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time since last step invocation
        """
        for script in self.__scripts:
            script_globals = self.prepare_globsl()
            script.__dict__.update(script_globals)
            script.step(time_delta)

    def eval(self, string):
        script_globals = self.prepare_globsl()
        return eval(string, script_globals)
    
    def add_script(self, name, filename):
        """Adds a script to the scripts dictionary
        
            Args:
                
                name: The name of the script
                
                filename: Path to the script file
        """
        script_file = file(filename, "r")
        script_module = imp.new_module(name)
        exec script_file in script_module.__dict__
        self.__scripts.append(script_module) 
        
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

        if scripts is not None:
            for script in scripts:
                name = script[0]
                filename = script[1]
                self.add_script(name, filename)
         
        
