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
import inspect

from bGrease.component import Component

from fife_rpg.components import ComponentManager
from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg.exceptions import NotRegisteredError

class ClassProperty(property):
    """Class to make class properties"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)() # pylint: disable=E1101

class Base(Component):
    """Base component for fife-rpg."""

    __registered_as = None
    dependencies = []

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
    def register(cls, name, auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        try:
            ComponentManager.register_component(name, cls())
            cls.__registered_as = name
            if auto_register:
                for sub_cls in inspect.getmro(cls):
                    if ((not (sub_cls is cls or sub_cls is Base))
                         and issubclass(sub_cls, Base)):
                        sub_cls.__registered_as = name
            for dependency in cls.dependencies:
                if not dependency.registered_as:
                    dependency.register()
            return True
        except AlreadyRegisteredError as error:
            print error
            return False
