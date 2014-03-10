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

"""Various functions and classes

.. module:: helpers
    :synopsis: Various functions and classes

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""


class ClassProperty(property):
    """Class to make class properties"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()  # pylint: disable=E1101


class Enum(set):
    """A enumeration type"""
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
