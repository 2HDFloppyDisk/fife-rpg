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

"""The look action prints the description of the target

.. module:: look
    :synopsis: Prints the description of the target
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import
from fife_rpg.actions.entity_action import EntityAction
from fife_rpg.components.description import Description


class Look(EntityAction):
    """Action for unlocking lockables"""

    dependencies = [Description]

    def execute(self):
        """Execute the action

        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.

        Returns: A text describing the target.
        """
        description = getattr(self.target, Description.registered_as)
        # pylint: disable=E0602
        text = _("You see %s. \n%s") % (_(description.view_name),
                                        _(description.desc))
        # pylint: enable=E0602
        EntityAction.execute(self)
        return text

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
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        description = getattr(entity, Description.registered_as)
        if description:
            return True
        return False

    @classmethod
    def register(cls, name="Look"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return super(Look, cls).register(name)
