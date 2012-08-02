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

#  This module is based on the character statistics system from PARPG

"""The character statistics system manages the character statistics.

.. module:: character_statistics
    :synopsis: Manages the character statistics
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.systems import Base
from fife_rpg.entities import RPGEntity
from fife_rpg.components.character_statistics import CharacterStatistics


class NoSuchStatisticError(Exception):
    """Exception that gets raised when a statistic was tried to be accessed that
    does not exist
    
    Properties:        
        name: The name of the statistic
    """
    
    def __init__(self, name):
        Exception.__init__(self)
        self.name = name
    
    def __str__(self):
        """Returns the message of the Exception"""
        return "There is no %s statistic" % (self.name)
    
class NoStatisticComponentError(Exception):
    """Exception that gets raised when an entity does not have a
    character_statistics component
    
    Properties:
        entity: The entity
    """
    
    def __init__(self, entity):
        Exception.__init__(self)
        self.entity = entity

    def __str__(self):
        """Returns the message of the Exception"""
        return ("The %s entity does not have character statistics" %
                self.entity.identifier)
        
class Statistic(object):
    """Class to store the data about a statistic
    
    Properties:
        name: The internal name of the statistic
        view_name: The displayed name of the statistic
        description: The description of the statistic
    """
    
    def __init__(self, name, view_name, description):
        self.name = name
        self.view_name = view_name

class CalculatedStatistic(Statistic):
    """Class to store the data about a calculated statistic
    
    Properties:
        name: The internal name of the statistic
        view_name: The displayed name of the statistic
        formula: How the statistic is calculated
        description: The description of the statistic
    """
    
    def __init__(self, name, view_name, description, formula):
        Statistic.__init__(self, name, view_name, description)
        self.formula = formula

class CharacterStatisticSystem(Base):
    """The game environment system manages what variables and functions are 
    available to scripts.
    
    Properties:
        primary_statistics: Dictionary holding the primary statistics
        secondary_statistics: Dictionary holfing the secondary statistics
    """

    dependencies = [CharacterStatistics]

    @classmethod
    def register(cls, name="character_statistics", *args, **kwargs):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered
            *args: Additional arguments to pass to the class constructor
            **kwargs: Additional keyword arguments to pass to the class 
            constructor

        Returns:
            True if the system was registered, False if not.
        """
        (super(CharacterStatisticSystem, cls).register(name, **kwargs))
        
    def __init__(self, primary_statistics=None, secondary_statistics=None):
        Base.__init__(self)
        self.primary_statistics = primary_statistics or {}
        self.secondary_statistics= secondary_statistics or {}
    
    def get_statistic_value(self, entity, statistic):
        """Get the entities value of the given statistic
        
        Args:
            entity: An RPGEntity or the name of the entity
            statistic: The internal name of the statistic
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)      
        if self.primary_statistics.has_key(statistic):
            statistics = getattr(entity, CharacterStatistics.registered_as)
            try:
                return statistics.primary_stats[statistic]
            except KeyError:
                return 0
        elif self.secondary_statistics.has_key(statistic):
            statistics = getattr(entity, CharacterStatistics.registered_as)
            try:            
                return statistics.secondary_stats[statistic]
            except KeyError:
                return 0
        else:
            NoSuchStatisticError(statistic)
    
    def get_primary_statistic_values(self, entity):
        """Collects and returns the values of the primary statitistic values
        of the entity.
        
        Args:
            entity: An RPGEntity or the name of the entity
        
        Returns:
            A dictionary containing the statistic short names and the values
            for that entity
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        primary_statistics = {}
        for statistic in self.primary_statistics.iterkeys():
            value = self.get_statistic_value(entity, statistic)
            primary_statistics[statistic] = value
        return primary_statistics

    def get_secondary_statistic_values(self, entity):
        """Collects and returns the values of the secondary statitistic values
        of the entity.
        
        Args:
            entity: An RPGEntity or the name of the entity
        
        Returns:
            A dictionary containing the statistic short names and the values
            for that entity
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        secondary_statistics = {}
        for statistic in self.secondary_statistics.iterkeys():
            value = self.get_statistic_value(entity, statistic)
            secondary_statistics[statistic] = value
        return secondary_statistics

    def get_statistic_values(self, entity):
        """Collects and returns the combined values of the primary and secondary 
        statitistic values of the entity.
        
        Args:
            entity: An RPGEntity or the name of the entity
        
        Returns:
            A dictionary containing the statistic short names and the values
            for that entity
        """
        statistics = {}
        statistics.update(self.get_primary_statistic_values(entity))
        statistics.update(self.get_secondary_statistic_values(entity))
        return statistics
        
    def step(self, time_delta): #pylint: disable=W0613
        """Execute a time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time elapsed since last step
        """
        comp_name = CharacterStatistics.registered_as
        entity_extent = getattr(self.world[RPGEntity], comp_name)
        for entity in entity_extent:
            stats_component = getattr(entity, comp_name) 
            values = self.get_statistic_values(entity)
            comp_secondary_stats = stats_component.secondary_stats            
            for statistic_name, statistic in self.secondary_statistics.iteritems():
                value = eval(statistic.formula, values)
                comp_secondary_stats[statistic_name] = value