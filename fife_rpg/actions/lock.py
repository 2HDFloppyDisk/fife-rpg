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

#  This module is based on the scriptingsystem module from PARPG

"""The lock action locks closed lockables

.. module:: lock
    :synopsis: Locks closed lockables
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
from fife_rpg.actions.entity_action import EntityAction
from fife_rpg.components.lockable import Lockable
from fife_rpg.components.lockable import lock_lock


class Lock(EntityAction):
    """Action for locking lockables"""

    dependencies = [Lockable]

    def execute(self):
        """Execute the action

        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.
        """
        lockable = getattr(self.target, Lockable.registered_as)
        lock_lock(lockable)
        EntityAction.execute(self)

    @classmethod
    def check_performer(cls, entity):  # pylint: disable=W0613
        """Checks whether the entity qualifies as an performer for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return True

    @classmethod
    def check_target(cls, entity):  # pylint: disable=W0613
        """Checks whether the entity qualifies as a target for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.rpg_application.RPGApplication` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        lockable = getattr(entity, Lockable.registered_as)
        if lockable and (lockable.closed and not lockable.locked):
            return True
        return False

    @classmethod
    def register(cls, name="Lock"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return super(Lock, cls).register(name)
