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

"""The read action prints the text of a readable

.. module:: read
    :synopsis: Prints the text of a readable
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from abc import ABCMeta, abstractmethod

from fife_rpg.actions.base import Base


class BaseReturn(Base):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, application, agent, target, commands=None):
        Base.__init__(application, agent, target, commands)    
       
       
    @abstractmethod
    def get_values(self):
        """Returns the values of the action"""
        pass
    
    def execute(self, callback=None):
        """Execute the action
        
        Args:
            callback: If set this function will get called with the returned
            values.
             
        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.

        Returns:
            The text of the readable
        """
        values = self.get_values()
        Base.execute(self)
        if callback is not None:
            callback(values)
        return values

