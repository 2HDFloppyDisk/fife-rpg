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

"""This module manages commands for the console.

.. module:: console_commands
    :synopsis: Manages commands for the console.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from copy import copy

from fife_rpg.exceptions import AlreadyRegisteredError

__COMMANDS = {}


def register_command(name, function):
    """Registers a function as a command

    Args:
        name: The keyword for the command
        function: The function to call
    """
    if name in __COMMANDS:
        raise AlreadyRegisteredError(name, "Command")
    __COMMANDS[name] = function


def get_commands():
    """Returns a copy of the commands"""
    return copy(__COMMANDS)
