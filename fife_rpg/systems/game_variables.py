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
"""The game variables system manages game variables.

.. module:: game_variables
    :synopsis: Manages game variables.
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import copy

from fife_rpg.systems import Base
from fife_rpg.console_commands import register_command
from fife_rpg.exceptions import AlreadyRegisteredError


class GameVariables(Base):

    """The game environment system manages what variables and functions are
    available to scripts.
    """

    __callbacks = []

    @classmethod
    def register(cls, name="game_variables"):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the system was registered, False if not.
        """
        return super(GameVariables, cls).register(name)

    @classmethod
    def add_callback(cls, callback):
        """Adds a callback function to the GameVariables

        Args:
            callback: The function to add
        """
        cls.__callbacks.append(callback)

    def __init__(self):
        Base.__init__(self)
        self.__dynamic = {}
        self.__static = {}

    def get_variables(self):
        """Returns the the variables as a dictionary"""
        vals = copy(self.__static)
        vals.update(self.__dynamic)
        return vals

    def set_variable(self, name, value, allow_static_hide=False):
        """Sets a dynamic variable to the specified value

        Args:
            name: The name of the variable

            value: The value the variables should be set to

            allow_static_hide: If set to True the function will allow setting
            the value even if there is already a static variable with this
            name. The static value will then be hidden, but not deleted.

        Returns:
            The (new) value of the variable or an error string.
        """
        if not allow_static_hide:
            if name not in self.__dynamic and name in self.__static:
                return "There is already a %s static variable" % (name)
        self.__dynamic[name] = value
        return self.__dynamic[name]

    def delete_variable(self, name):
        """Deletes a dynamic variable

        Args:
            name: The name of the varriable

        Returns: None or an error message
        """
        if name in self.__dynamic:
            del self.__dynamic[name]
        else:
            return "There was no %s dynamic variable" % name

    def get_variable(self, name):
        """Returns the value of a variable

        Args:
            name: The name of the variable

        Raises:
            NameError: If there is no variable with that name
        """
        variables = self.get_variables()
        if name not in variables:
            raise NameError("Name '%s' is not defined" % name)
        return variables[name]

    def step(self, time_delta):  # pylint: disable= W0613
        """Execute a time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time since last step invocation
        """
        for callback in self.__callbacks:
            callback(self.__static)


# pylint: disable=C0111
# register console commmands
def __set_variable_console(application, *args):
    if not GameVariables.registered_as:
        return "The GameVariables system is not active."
    game_variables = getattr(application.world.systems,
                             GameVariables.registered_as)
    try:
        return game_variables.set_variable(*args)
    except TypeError as error:
        return str(error).replace("set_variable()", "SetVariable")

try:
    register_command("SetVariable", __set_variable_console)
except AlreadyRegisteredError:
    pass


def __delete_variable_console(application, *args):
    if not GameVariables.registered_as:
        return "The GameVariables system is not active."
    game_variables = getattr(application.world.systems,
                             GameVariables.registered_as)
    try:
        return game_variables.delete_variable(*args)
    except TypeError as error:
        return str(error).replace("delete_variable()", "DeleteVariable")

try:
    register_command("DeleteVariable", __delete_variable_console)
except AlreadyRegisteredError:
    pass


def __get_variable_console(application, *args):
    if not GameVariables.registered_as:
        return "The GameVariables system is not active."
    game_variables = getattr(application.world.systems,
                             GameVariables.registered_as)
    try:
        return str(game_variables.get_variable(*args))
    except TypeError as error:
        return str(error).replace("get_variable()", "GetVariable")
    except NameError as error:
        return str(error)

try:
    register_command("GetVariable", __get_variable_console)
except AlreadyRegisteredError:
    pass
