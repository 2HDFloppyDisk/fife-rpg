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

# This is based on the PARPG components package

"""This contains the general components used by fife-rpg

.. module:: components
    :synopsis: The general components used by fife-rpg

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from copy import deepcopy

from fife_rpg.exceptions import AlreadyRegisteredError

_components = {} # pylint: disable-msg=C0103

def get_components():
    """Returns the registered components"""
    return deepcopy(_components)

def register_component(component_name, component_class):
    """Registers an component
    
    Args:
        component_name: The name of the component_class
        component_class: The class of the component
        """
    if not component_name in _components:
        _components[component_name] = component_class
    else:
        raise AlreadyRegisteredError(component_name,  "component")
