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

"""This module contains functions for managing systems

.. module:: system_manager
    :synopsis: Functions for managing systems

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import deepcopy

from fife_rpg.exceptions import AlreadyRegisteredError, NotRegisteredError

_SYSTEMS = {}


def get_systems():
    """Returns the registered systems"""
    return deepcopy(_SYSTEMS)


def register_system(system_name, system_object):
    """Registers an system

    Args:
        system_name: The name of the system_object

        system_object: A bGrease system object
    """
    if system_name not in _SYSTEMS:
        _SYSTEMS[system_name] = system_object
    else:
        raise AlreadyRegisteredError(system_name, "system")


def unregister_system(system_name):
    """Unregister a system

    Args:
        system_name: The name of the system
    """
    if system_name in _SYSTEMS:
        del _SYSTEMS[system_name]
    else:
        raise NotRegisteredError("system")


def clear_systems():
    """Removes all registered systems"""
    for system in get_systems().values():
        system.unregister()
