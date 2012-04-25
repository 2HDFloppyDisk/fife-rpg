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

"""The base component and functions

.. module:: base
    :synopsis: The base component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from bGrease.component import Component
from fife_rpg.components import ComponentManager

class ClassProperty(property):
    """Class to make class properties"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class Base(Component):
    """Base component for fife-rpg."""

    __registered_as = None

    @ClassProperty
    @classmethod
    def registered_as(cls):
        """Returns the value of registered_as"""
        return cls.__registered_as

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        return self.fields.keys()

    @classmethod
    def register(cls, name):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the component was registered, False if not.
        """
        try:
            ComponentManager.register_component(name, cls())
            cls.__registered_as = name
            return True
        except ComponentManager.AlreadyRegisteredError as error:
            print error
            return False
