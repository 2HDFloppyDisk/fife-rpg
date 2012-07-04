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
    """Component that defines character statistics."""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, gender=str, picture=str, age=int, origin=str, 
                      primary_stats=dict, secondary_stats=dict, traits=list, 
                      )

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        fields.remove("primary_stats")
        fields.remove("secondary_stats")
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

def get_statistic(stats, name):
    """Gets the statistic by its name

    Args:
        name: The name of the statistic.

    Returns:
        The statistic with the given name or None
    """
    if name in stats.primary_stats:
        return stats.primary_stats[name]
    elif name in stats.secondary_stats:
        return stats.secondary_stats[name]
    else:
        for stat in stats.primary_stats:
            if stat.statistic_type.short_name == name:
                return stat
    return None

def get_stat_values(char_stats):
    """Gets the values of the stats as a dictionary.

    Args:
        char_stats: A CharacterStatistics instance.

    Returns:
        The values of the statistics in a dictionary.
    """
    stats = {"primary":{}, "secondary":{}}
    for name, stat in char_stats.primary_stats.iteritems():
        stats["primary"][name] = stat.value
    for name, stat in char_stats.secondary_stats.iteritems():
        stats["secondary"][name] = stat.value
    return stats
