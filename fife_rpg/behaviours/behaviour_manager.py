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

#  This module is based on the behaviour package from PARPG

"""This module manages the behaviours of fife-rpg agents.

.. module:: behaviours
    :synopsis: Manages the behaviours of fife-rpg agents.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from copy import copy

from fife_rpg.exceptions import AlreadyRegisteredError, NotRegisteredError

_BEHAVIOURS = {}


def register_behaviour(name, behaviour):
    """Registers a behaviour

    Args:
        name: The name of the behaviour

        behaviour: The behaviour class

    Raises:
        AlreadyRegisteredError if there is already a behaviour with that name
    """
    if name in _BEHAVIOURS:
        raise AlreadyRegisteredError(name, "behaviour")
    else:
        _BEHAVIOURS[name] = behaviour


def get_behaviours():
    """Returns a copy of the behaviour dictionary"""
    return copy(_BEHAVIOURS)


def get_behaviour(name):
    """Returns the behaviour with the given name"""
    if name in _BEHAVIOURS:
        return _BEHAVIOURS[name]
    return None


def unregister_behaviour(behaviour_name):
    """Unregister a behaviour

    Args:
        behaviour_name: The name of the behaviour
    """
    if behaviour_name in _BEHAVIOURS:
        del _BEHAVIOURS[behaviour_name]
    else:
        raise NotRegisteredError("behaviour")


def clear_behaviours():
    """Removes all registered behaviours"""
    for behaviour in get_behaviours().values():
        behaviour.unregister()
