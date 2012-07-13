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

from fife_rpg.components import ComponentManager
from fife_rpg.components.base import Base
from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg.exceptions import NotRegisteredError

class Lockable(Base):
    """Component that stores the data of a lock"""

    def __init__(self):
        """Constructor"""
        Base.__init__(self, closed=bool, locked=bool, 
                      open_animation=str, opened_animation=str,
                      close_animation=str, closed_animation=str)
        self.fields["open_animation"].default = lambda: "open"
        self.fields["opened_animation"].default = lambda: "opened"
        self.fields["close_animation"].default = lambda: "close"
        self.fields["closed_animation"].default = lambda: "closed"

    @classmethod
    def register(cls, name="lockable", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Lockable, cls).register(name, auto_register))

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

def lock_lock(lockable):
    """Lock the given lockable.

    Args:
        lockable: A Lockable instance

    Raises:
        OpenError if the lockable is open.
    """
    if not lockable.closed:
        raise OpenError
    lockable.locked = True    

def unlock_lock(lockable):
    """Unlock the given lockable

    Args:
        lockable: A Lockable instance
    """
    lockable.locked = False

def open_lock(lockable):# pylint: disable-msg=W0622
    """Open the lockable, if its unlocked.

    Args:
        lockable: A Lockable instance

    Raises:
        LockedError if the lockable is locked
    """
    if lockable.locked:
        raise LockedError
    lockable.closed = False

def close_lock(lockable):
    """Close the lockable.

    Args:
        lockable: A lockable instance
    """
    lockable.closed = True


def check_lockable_fifeagent(fifeagent, lockable):
    """Checks the lockable for inconsistences with the fifeagent"""
    if lockable.closed:
        fifeagent.behaviour.animate(lockable.closed_animation, repeating=True)
    else:
        fifeagent.behaviour.animate(lockable.opened_animation, repeating=True)
        
def register_checkers():
    """Registers the components checkers"""
    if not Lockable.registered_as:
        raise NotRegisteredError("Lockable")
    if FifeAgent.registered_as:
        ComponentManager.register_checker(
            (FifeAgent.registered_as, Lockable.registered_as),
            check_lockable_fifeagent)
