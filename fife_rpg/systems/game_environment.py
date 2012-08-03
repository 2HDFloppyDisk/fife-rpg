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

.. module:: game_environment
    :synopsis: Manages the game environment
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.systems import Base


class GameEnvironment(Base):
    """The game environment system manages what variables and functions are 
    available to scripts.    
    """

    @classmethod
    def register(cls, name="game_environment", *args, **kwargs):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered
            
            args: Additional arguments to pass to the class constructor
            
            kwargs: Additional keyword arguments to pass to the class 
            constructor

        Returns:
            True if the system was registered, False if not.
        """
        return (super(GameEnvironment, cls).register(name, *args, **kwargs))
        
    def __init__(self):
        Base.__init__(self)
        self.__locals = {}
        self.__callbacks = []
        self.__globals = {}
        
    def add_callback(self, callback):
        """Adds a callback function to the GameEnvironment
        
        Args:
            callback: The function to add
        """
        self.__callbacks.append(callback)
        
    def get_environement(self):
        """Returns the environment as a 2 dictionaries"""
        return self.__globals, self.__locals
        
    def step(self, time_delta): #pylint: disable= W0613
        """Execute a time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time since last step invocation
        """
        for callback in self.__callbacks:
            callback(self.__globals)