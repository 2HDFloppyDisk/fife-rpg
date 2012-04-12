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

#  This module is based on the action module from PARPG

"""This module manages the actions of fife-rpg.

An action is a object that can be executed later. This can be used, 
for example, in menus,

.. module:: action
    :synopsis: Manages the actions of fife-rpg

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from copy import deepcopy

class AlreadyRegisteredError(Exception):
    """Exception that gets raised when an object with the name is already
    registered"""
    def __init__(self, name, type):
        """Constructor
        
        Args:
            name: The name of the action that was already registered
            type: The type of the object
        """
        self.name = name
        self.type = type
    
    def __str__(self):
        """Returns the message of the Exception"""
        return "An %s with the name '%s' already exists" % (self.type,  self.name)

class NoSuchCommandError(Exception):
    """Exception that gets raised when the command is not found"""
    def __init__(self, name):
        """Constructor
        
        Args:
            name: The name of the command that was being tried to execute
        """
        self.name = name
    
    def __str__(self):
        """Returns the message of the Exception"""
        return "There is no '%s' command" % (self.name)

_actions = {}
_commands = {}

class Action(object):
    """Base Action class, to define the structure"""

    def __init__(self, controller, commands = None):
        """Basic action constructor

        Args:
            controller: A fife_rpg.ControllerBase instance
        """
        self.commands = commands or ()
        self.controller = controller
        self.executed = False
    
    def execute(self):
        """Execute the action
        
        Raises:
            NoSuchCommandError if there is no command with the name
        """
        #Check if there are special commands and execute them
        for command_data in self.commands:
            command = command_data["Command"]
            if command in _commands:
                _commands[command](command_data)
            else:
                raise NoSuchCommandError(command)
        self.executed = True

def get_actions():
    """Returns the registered actions"""
    return deepcopy(_actions)

def register_action(action_name, action_class):
    """Registers an action
    
    Args:
        action_name: The name of the action_class
        action_class: The class of the action
        """
    if not action_name in _actions:
        _actions[action_name] = action_class
    else:
        raise AlreadyRegisteredError(action_name,  "action")

def get_commands():
    """Returns the registered commands"""
    return deepcopy(_commands)

def register_command(command_name, function):
    """Registers an command
    
    Args:
        command_name: The name of the command_class
        function: The function to execute
        """
    if not command_name in _commands:
        _commands[command_name] = function
    else:
        raise AlreadyRegisteredError(command_name, "command")
