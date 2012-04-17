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

"""The Lockable component and functions

.. module:: lockable
    :synopsis: The Lockable component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class Lockable(Base):
    """Component that stores the data of a lock"""

    __registered_as = ""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, closed=bool, locked=bool)

    @classmethod
    def register(cls, name="lockable"):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the component was registered, False if not.
        """
        if (super(Lockable, cls).register(name)):
            cls.__registered_as = name
            return True
        return False

class LockedError(Exception):
    """Error that is raised when the lock is locked"""

    def __str__(self):
        """Returns the string representing the exception"""
        return "Is locked"

class OpenError(Exception):
    """Error that is raised when the lock is open"""

    def __str__(self):
        """Returns the string representing the exception"""
        return "Is open"

def lock(lockable):
    """Lock the given lockable.

    Args:
        lockable: A Lockable instance

    Raises:
        OpenError if the lockable is open.
    """
    if not lockable.closed:
        raise OpenError
    lockable.locked = True    

def unlock(lockable):
    """Unlock the given lockable

    Args:
        lockable: A Lockable instance
    """
    lockable.locked = False

def open(lockable):# pylint: disable-msg=W0622
    """Open the lockable, if its unlocked.

    Args:
        lockable: A Lockable instance

    Raises:
        LockedError if the lockable is locked
    """
    if lockable.locked:
        raise LockedError
    lockable.closed = False

def close(lockable):
    """Close the lockable.

    Args:
        lockable: A lockable instance
    """
    lockable.closed = True
