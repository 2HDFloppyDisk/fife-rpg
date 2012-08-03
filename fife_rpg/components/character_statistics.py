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

"""CharacterStatistics component and functions

.. module:: character_statistics
    :synopsis: CharacterStatistics component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class CharacterStatistics(Base):
    """Component that defines character statistics.
    
    Fields:
        gender: The gender of the character
        
        picture: The identifier portrait picture
        
        age: The age of the character
        
        origin: The origin of the character
        
        primary_stats: The primary, directly increasable statistics
        
        secondary_stats: The secondary, calculated statistics
        
        stat_points: The points that can be used to raise stats
        
        traits: The characters traits
    """

    def __init__(self):
        Base.__init__(self, gender=str, picture=str, age=int, origin=str, 
                      primary_stats=dict, secondary_stats=dict, stat_points=int,
                      traits=list, 
                      )

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        return fields

    @classmethod
    def register(cls, name="char_stats", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """        
        return (super(CharacterStatistics, cls).register(name, auto_register))
