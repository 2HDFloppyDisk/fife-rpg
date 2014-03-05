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

"""This module contains the exceptions from fife-rpg.

.. module:: exceptions
    :synopsis: Contains the exceptions from fife-rpg.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""


class AlreadyRegisteredError(Exception):
    """Exception that gets raised when an object with the name is already
    registered

    Properties:
        name: The name of the action that was already registered

        obj_type: The obj_type of the object
    """

    def __init__(self, name, obj_type):
        Exception.__init__(self)
        self.name = name
        self.type = obj_type

    def __str__(self):
        """Returns the message of the Exception"""
        return ("A(n) %s with the name '%s' already exists" %
                    (self.type, self.name))

class NotRegisteredError(Exception):
    """Exception that gets raised when a class is not registered

    Properties:
        obj_type: The obj_type of the object
    """

    def __init__(self, obj_type):
        Exception.__init__(self)
        self.type = obj_type

    def __str__(self):
        """Returns the message of the Exception"""
        return ("%s class not registered." %
                    (self.type))

class NoSuchCommandError(Exception):
    """Exception that gets raised when the command is not found

    Properties:
        name: The name of the command that was being tried to execute
    """

    def __init__(self, name):
        Exception.__init__(self)
        self.name = name

    def __str__(self):
        """Returns the message of the Exception"""
        return "There is no '%s' command" % (self.name)
