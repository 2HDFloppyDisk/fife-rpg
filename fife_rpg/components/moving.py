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

"""The moving component and functions

.. module:: moving
    :synopsis: The Moving component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class Moving(Base):
    """Component that stores the values for agents that can move around
    the map by using pathfinding.
    
    Fields:
        walk_speed: The walking speed
        
        walk_action: The animation that is played when walking
        
        run_speed: The Running speed
        
        run_action: The animation that is played when running
    """

    def __init__(self):
        Base.__init__(self, walk_speed=float, walk_action=str,
                      run_speed=float, run_action=str)
        self.fields["walk_speed"].default = lambda: 0.0 
        self.fields["walk_action"].default = lambda: "walk"
        self.fields["run_speed"].default = lambda: 0.0 
        self.fields["run_action"].default = lambda: "run"

    @classmethod
    def register(cls, name="Moving", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Moving, cls).register(name, auto_register))