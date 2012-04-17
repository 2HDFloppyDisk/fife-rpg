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

#  This package is based on the entities package from PARPG

"""This package contains the entities for the component system.

.. module:: entities
    :synopsis: Contains the entities for the component system.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import sys

from fife_rpg.entities.general import General

def create_entity(info, identifier, world, extra = None):
    """Called when we need to get an actual object.

        Args:
            info: Stores information about the object we want to create
            identifier: The unique identifier of the new object
            world: The world the new entity will belong to.
            extra: Stores additionally required attributes

        Returns:
            The created entity.
       """
    extra = extra or {}

    for key, val in extra.items():
        info[key].update(val)

    new_ent = General(world, identifier)
    for component, data in info.items():
        comp_obj = getattr(new_ent, component)
        for key, value in data.items():
            setattr(comp_obj, key, value)
    return new_ent
