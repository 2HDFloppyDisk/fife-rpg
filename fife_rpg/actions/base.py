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

"""Base class for actions

.. module:: base
    :synopsis: The base action

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import print_function

from builtins import object
from fife_rpg.exceptions import (NoSuchCommandError, AlreadyRegisteredError,
                                 NotRegisteredError)
from fife_rpg.actions import ActionManager
from fife_rpg.helpers import ClassProperty


class BaseAction(object):
    """Base class for actions

    Properties:
        application: A :class:`fife_rpg.rpg_application.RPGApplication`

        commands: List of additional commands to execute

        registered_as: Class property that sets under what name the class is
        registered

        dependencies: Class property that sets the classes this System depends
        on
    """
    __registered_as = None
    dependencies = []

    def __init__(self, application, commands=None):
        self.commands = commands or ()
        self.application = application
        self.executed = False

    def execute(self):
        """Execute the action

        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.
        """
        # Check if there are special commands and execute them
        for command_data in self.commands:
            command = command_data["Command"]
            available_commands = ActionManager.get_commands()
            if command in available_commands:
                available_commands[command](command_data)
            else:
                raise NoSuchCommandError(command)
        self.executed = True

    @classmethod
    def register(cls, name):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        try:
            ActionManager.register_action(name, cls)
            cls.__registered_as = name
            for dependency in cls.dependencies:
                if not dependency.registered_as:
                    dependency.register()
            return True
        except AlreadyRegisteredError as error:
            print(error)
            return False

    @classmethod
    def unregister(cls):
        """Unregister an action class

        Returns:
            True if the action was unregistered, false if Not
        """
        try:
            ActionManager.unregister_action(cls.__registered_as)
            cls.__registered_as = None
            return True
        except NotRegisteredError as error:
            print(error)
            return False

    @ClassProperty
    @classmethod
    def registered_as(cls):
        """Returns the value of registered_as"""
        return cls.__registered_as
