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

"""The open actions opens unlocked lockables

.. module:: open
    :synopsis: Opens unlocked lockables
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.actions.entity_action import EntityAction
from fife_rpg.components.lockable import Lockable
from fife_rpg.components.lockable import open_lock
from fife_rpg.components.fifeagent import FifeAgent


class Open(EntityAction):
    """Action for opening unlocked lockables"""

    dependencies = [Lockable]

    def execute(self):
        """Execute the action

        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.
        """
        lockable = getattr(self.target, Lockable.registered_as)
        open_lock(lockable)
        if FifeAgent.registered_as:
            fifeagent_data = getattr(self.target, FifeAgent.registered_as)
            if fifeagent_data:
                behaviour = fifeagent_data.behaviour
                behaviour.act(lockable.open_action)
                behaviour.queue_action(lockable.opened_action,
                                          repeating=True)

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
        if lockable and (not lockable.locked and lockable.closed):
            return True
        return False

    @classmethod
    def register(cls, name="Open"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return super(Open, cls).register(name)
