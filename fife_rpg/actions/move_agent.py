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

"""The move_agent action switches to a different map

.. module:: move_agent
    :synopsis: Switches to a different map
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.actions.entity_action import EntityAction
from fife_rpg.components.move_agent import MoveAgent as MoveAgentComponent
from fife_rpg.components.agent import Agent


class MoveAgent(EntityAction):
    """Positions the agent on a new map, layer and/or position"""

    dependencies = [MoveAgentComponent, Agent]

    def execute(self):
        """Execute the action

        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.
        """
        move_agent = getattr(self.target, MoveAgent.registered_as)
        agent = getattr(self.performer, Agent.registered_as)
        agent.new_map = move_agent.target_map
        agent.new_position = move_agent.target_position
        agent.new_layer = move_agent.target_layer
        EntityAction.execute(self)

    @property
    def menu_text(self):
        """Returns the text that is to be displayed in menus"""
        return "Change Map"

    @classmethod
    def check_performer(cls, entity):  # pylint: disable-msg=W0613
        """Checks whether the entity qualifies as an performer for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        agent = getattr(entity, Agent.registered_as)
        if agent:
            return True
        return False

    @classmethod
    def check_target(cls, entity):  # pylint: disable-msg=W0613
        """Checks whether the entity qualifies as a target for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        move_agent = getattr(entity, MoveAgent.registered_as)
        if move_agent:
            return True
        return False

    @classmethod
    def register(cls, name="MoveAgent"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return super(MoveAgent, cls).register(name)
