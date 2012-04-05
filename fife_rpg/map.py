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

"""This module contains everything for handling fife-rpg maps

.. module:: map
    :synopsis: contains everything for handling fife-rpg maps.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

class NoSuchRegionError(Exception):
    """Gets thrown when the code tried to access a region that does not exits 
    on the map."""
    
    def __init__(self, map_name, region_name):
        """Constructor
        
        Args:
            map_name: The name of the map_name
            region_name: The name of the region_name
        """
        Exception.__init__(self)
        self.map = map_name
        self.region = region_name
    
    def __str__(self):
        """Returns a string representing the exception"""
        return ("The map '%s' has no region called '%s'." % 
                    (self.map,  self.region))

class Map(object):
    """Contains the data of a map"""

    def __init__(self, fife_map, name, regions):
        """Constructor

        Args:
            fife_map: A fife.Map instance, representing the fife_map
            name: The name of the fife_map.
            regions: A dictionary that defines specific regions on the fife_map, as
            fife.DoubleRect instances.
        """
        self.__map = fife_map
        self.__name = name
        self.__regions = regions

    @property
    def map(self):
        """Returns the fife.Map"""
        return self.__map

    @property
    def name(self):
        """Returns the name of the map"""
        return self.__name

    @property
    def regions(self):
        """Returns the regions of the map"""
        return self.__regions
        
    def is_in_region(self, location, region):
        """Checks if a given point is inside the given region
        
        Args:
            location: A fife.DoublePoint instance
            region: The name of the region
            
        Raises:
            NoSuchRegionError: The specified region does not exist.
        """
        if not region in self.regions:
            raise NoSuchRegionError(self.name,  region)
        else:
            return self.regions[region].contains(location)
