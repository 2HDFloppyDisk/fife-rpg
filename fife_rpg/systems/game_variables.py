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

"""The game environment system manages what variables and functions are 
available to scripts.

.. module:: game_variables
    :synopsis: Manages the game environment
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import copy

from fife_rpg.systems import Base
from fife_rpg.console_commands import register_command

class GameVariables(Base):
    """The game environment system manages what variables and functions are 
    available to scripts.    
    """

    @classmethod
    def register(cls, name="game_variables"):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the system was registered, False if not.
        """
        return (super(GameVariables, cls).register(name))
        
    def __init__(self):
        Base.__init__(self)
        self.__dynamic = {}
        self.__static = {}
        self.__callbacks = []
        
    def add_callback(self, callback):
        """Adds a callback function to the GameVariables
        
        Args:
            callback: The function to add
        """
        self.__callbacks.append(callback)
        
    def get_variables(self):
        """Returns the the variables as a dictionary"""
        vals = copy(self.__static)
        vals.update(self.__dynamic)
        return vals
    
    def step(self, time_delta): #pylint: disable= W0613
        """Execute a time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time since last step invocation
        """
        for callback in self.__callbacks:
            callback(self.__static)