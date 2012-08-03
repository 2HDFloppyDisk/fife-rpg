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

"""The base system and functions

.. module:: base
    :synopsis: The base system and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from bGrease import System

from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg.systems import SystemManager
from fife_rpg.helpers import ClassProperty

class Base(System):
    """Base system for fife-rpg.
    
    Properties:
        registered_as: Class property that sets under what name the class is
        registered
        
        dependencies: Class property that sets the classes this System depends on
    """

    __registered_as = None
    dependencies = []

    @ClassProperty
    @classmethod
    def registered_as(cls):
        """Returns the value of registered_as"""
        return cls.__registered_as

    @classmethod
    def register(cls, name, *args, **kwargs):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered
            args: Additional arguments to pass to the class constructor
            kwargs: Additional keyword arguments to pass to the class 
            constructor

        Returns:
            True if the system was registered, False if not.
        """
        try:
            for dependency in cls.dependencies:
                if not dependency.registered_as:
                    dependency.register()
            SystemManager.register_system(name, cls(*args, **kwargs))
            cls.__registered_as = name
            return True
        except AlreadyRegisteredError as error:
            print error
            return False

