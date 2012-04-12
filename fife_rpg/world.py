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

# This module is based on the PARPGWorld class.

"""This module contains the world class used used by the entity system.

.. module:: world
    :synopsis: Contains the world class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from bGrease.grease_fife.world import World

from fife_rpg.components import get_components

class RPGWorld(World):
    """The Base world for all rpgs.
    
    Sets up the generic systems and components"""

    def __init__(self, engine):
        """Constructor

        Args:
            engine: a fife.Engine instance
        """
        World.__init__(self, engine)
    
    def configure(self):
        """Configure the worlds components and systems"""
        World.configure(self)
        components = get_components()
        for name, component in components.iteritems():
            setattr(self.components, name, component)
        #TODO: Add the generic systems once they are finished
