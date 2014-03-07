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

"""This module contains functions for managing components

.. module:: component_manager
    :synopsis: Functions for managing components

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import copy

from fife_rpg.exceptions import AlreadyRegisteredError

_COMPONENTS = {}
_CHECKERS = []


def get_components():
    """Returns the registered components"""
    return copy(_COMPONENTS)


def register_component(component_name, component_object):
    """Registers an component

    Args:
        component_name: The name of the component_object

        component_object: A bGrease component object
    """
    if not component_name in _COMPONENTS:
        _COMPONENTS[component_name] = component_object
    else:
        raise AlreadyRegisteredError(component_name, "component")

def clear_components():
    """Removes all registered components"""
    _COMPONENTS.clear()

def get_checkers():
    """Returns the registered checkers"""
    return copy(_CHECKERS)


def register_checker(component_names, callback):
    """Add a checker to the checkers list

    Args:
        component_name: A list of the names of the components
        which the checker will check

        callback: The checker function
    """
    _CHECKERS.append((component_names, callback))

def clear_checkers():
    """Removes all checkers"""
    del _CHECKERS[:]
