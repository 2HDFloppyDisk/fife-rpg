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

"""The pick_up actions allows objects to be picked up from a map

.. module:: pick_up
    :synopsis: Allows objects to be picked up from a map
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.actions.entity_action import EntityAction
from fife_rpg.components.general import General
from fife_rpg.components.agent import Agent
from fife_rpg.components.containable import Containable
from fife_rpg.components.container import Container
from fife_rpg.components.container import put_item


class PickUp(EntityAction):

    """Action for picking up items from a map"""

    dependencies = [General, Agent, Containable, Container]

    def execute(self):
        """Execute the action

        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.
        """
        agent = getattr(self.target, Agent.registered_as)
        game_map = self.application.maps[agent.map]
        general = getattr(self.target, General.registered_as)
        game_map.remove_entity(general.identifier)
        game_map.update_entities()
        put_item(self.performer, self.target)
        super(PickUp, self).execute()

    @property
    def menu_text(self):
        """Returns the text that is to be displayed in menus"""
        return "Pick up"

    @classmethod
    def check_performer(cls, entity):  # pylint: disable=W0613
        """Checks whether the entity qualifies as an performer for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return bool(getattr(entity, Container.registered_as))

    @classmethod
    def check_target(cls, entity):  # pylint: disable=W0613
        """Checks whether the entity qualifies as a target for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return bool(getattr(entity, Containable.registered_as))

    @classmethod
    def register(cls, name="PickUp"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return super(PickUp, cls).register(name)
