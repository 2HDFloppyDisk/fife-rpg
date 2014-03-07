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

from fife_rpg.exceptions import AlreadyRegisteredError, NotRegisteredError

_ACTIONS = {}
_COMMANDS = {}


def get_actions():
    """Returns the registered actions"""
    return copy(_ACTIONS)


def get_possible_actions(performer, target):
    """Get the entity actions that can be performed with the performer and the
    target

    Args:
        performer: The performer initiating the action

        target: The target of the action

    Returns:
        A dictionary with the actions that can be performed using the performer
        and the target
    """
    from fife_rpg.actions.entity_action import EntityAction
    actions = get_actions()
    possible_actions = {}
    for name, action in actions.iteritems():
        if not issubclass(action, EntityAction):
            continue
        if action.check_performer(performer) and action.check_target(target):
            possible_actions[name] = action
    return possible_actions


def register_action(action_name, action_class):
    """Registers an action

    Args:
        action_name: The name of the action_class

        action_class: The class of the action

    Raises:
        :class:`fife_rpg.exceptions.AlreadyRegisteredError`
        if the action already exists.
    """
    if not action_name in _ACTIONS:
        _ACTIONS[action_name] = action_class
    else:
        raise AlreadyRegisteredError(action_name, "action")

def unregister_action(action_name):
    """Unregister an action

    Args:
        action_name: The name of the action
    """
    if action_name in _ACTIONS:
        del _ACTIONS[action_name]
    else:
        raise NotRegisteredError("action")

def clear_actions():
    """Removes all actions"""
    for action in get_actions().itervalues():
        action.unregister()

def get_commands():
    """Returns the registered commands"""
    return copy(_COMMANDS)


def register_command(command_name, function):
    """Registers an command

    Args:
        command_name: The name of the command_class

        function: The function to execute

    Raises:
        :class:`fife_rpg.exceptions.AlreadyRegisteredError`
        if the command already exists.
    """
    if not command_name in _COMMANDS:
        _COMMANDS[command_name] = function
    else:
        raise AlreadyRegisteredError(command_name, "command")


def clear_commands():
    """Removes all commands"""
    _COMMANDS.clear()
