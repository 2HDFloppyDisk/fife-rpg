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

"""The base action

.. module:: base
    :synopsis: The base action

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.exceptions import NoSuchCommandError, AlreadyRegisteredError
from fife_rpg.actions import ActionManager
from fife_rpg.helpers import ClassProperty

class Base(object):
    """Base Action class, to define the structure"""

    __registered_as = None
    dependencies = []

    def __init__(self, application, agent, target, commands = None):
        """Basic action constructor

        Args:
            application: A fife_rpg.RPGApplication instance
            agent: The agent initiating the action
            target: The target of the action
            commands: List of additional commands to execute
        """
        self.commands = commands or ()
        self.application = application
        self.agent = agent
        self.target = target
        self.executed = False
        
    @property
    def menu_text(self):
        """Returns the text that is to be displayed in menus"""
        return self.registered_as
    
    def execute(self):
        """Execute the action
        
        Raises:
            NoSuchCommandError if there is no command with the name
        """
        #Check if there are special commands and execute them
        for command_data in self.commands:
            command = command_data["Command"]
            available_commands = ActionManager.get_commands()
            if command in available_commands:
                available_commands[command](command_data)
            else:
                raise NoSuchCommandError(command)
        self.executed = True

    @classmethod
    def check_agent(cls, entity): #pylint: disable-msg=W0613
        """Checks whether the entity qualifies as an agent for this action
        
        Args:
            entity: The entity to ceck. A bGrease.Entity instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return False
    
    @classmethod
    def check_target(cls, entity): #pylint: disable-msg=W0613
        """Checks whether the entity qualifies as a target for this action
        
        Args:
            entity: The entity to ceck. A bGrease.Entity instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return False

    @classmethod
    def register(cls, name):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered
            *args: Additional arguments to pass to the class constructor
            **kwargs: Additional keyword arguments to pass to the class 
            constructor

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
            print error
            return False

    @ClassProperty
    @classmethod
    def registered_as(cls):
        """Returns the value of registered_as"""
        return cls.__registered_as