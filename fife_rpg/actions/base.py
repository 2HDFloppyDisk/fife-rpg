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

from fife_rpg.exceptions import NoSuchCommandError
from fife_rpg.actions import ActionManager

class Base(object):
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
            available_commands = ActionManager.get_commands()
            if command in available_commands:
                available_commands[command](command_data)
            else:
                raise NoSuchCommandError(command)
        self.executed = True

    @classmethod
    def check_entity(cls, entity): #pylint: disable-msg=W0613
        """Checks whether the action can be performed on the given entity
        
        Args:
            entity: The entity to ceck. A bGrease.Entity instance.

        Returns: True if the action can be performed on that entity. False 
        otherwise
        """
        return False