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

#  This module is based on the action module from PARPG

"""This module manages the actions of fife-rpg.

An action is a object that can be executed later. This can be used, 
for example, in menus,

.. module:: action
    :synopsis: Manages the actions of fife-rpg

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import copy

from fife_rpg.exceptions import AlreadyRegisteredError

_ACTIONS = {}
_COMMANDS = {}

def get_actions():
    """Returns the registered actions"""
    return copy(_ACTIONS)

def register_action(action_name, action_class):
    """Registers an action
    
    Args:
        action_name: The name of the action_class
        action_class: The class of the action

    Raises:
        AlreadyRegisteredError if the action already exists.
    """
    if not action_name in _ACTIONS:
        _ACTIONS[action_name] = action_class
    else:
        raise AlreadyRegisteredError(action_name,  "action")

def clear_actions():
    """Removes all actions"""
    _ACTIONS.clear()
    
def get_commands():
    """Returns the registered commands"""
    return copy(_COMMANDS)

def register_command(command_name, function):
    """Registers an command
    
    Args:
        command_name: The name of the command_class
        function: The function to execute

    Raises:
        AlreadyRegisteredError if the command already exists.
    """
    if not command_name in _COMMANDS:
        _COMMANDS[command_name] = function
    else:
        raise AlreadyRegisteredError(command_name, "command")

def clear_commands():
    """Removes all commands"""
    _COMMANDS.clear()
