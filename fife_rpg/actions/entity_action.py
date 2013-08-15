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

"""Base class for actions that an entity can perform on other entities.

.. module:: entity_action
    :synopsis: Base class for actions that an entity can perform on other
    entities.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.actions.base import BaseAction


class EntityAction(BaseAction):
    """Base class for actions that an entity can perform on other entities.

    Properties:
        application: A :class:`fife_rpg.rpg_application.RPGApplication`

        performer: The performer initiating the action

        target: The target of the action

        commands: List of additional commands to execute

        registered_as: Class property that sets under what name the class is
        registered

        dependencies: Class property that sets the classes this Action depends
        on
    """
    __registered_as = None
    dependencies = []

    def __init__(self, application, performer, target, commands=None):
        BaseAction.__init__(self, application, commands)
        self.commands = commands or ()
        self.application = application
        self.performer = performer
        self.target = target
        self.executed = False

    @property
    def menu_text(self):
        """Returns the text that is to be displayed in menus"""
        return self.registered_as

    @classmethod
    def check_performer(cls, entity):  # pylint: disable-msg=W0613
        """Checks whether the entity qualifies as an performer for this action

        Args:
            entity: The entity to ceck.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return False

    @classmethod
    def check_target(cls, entity):  # pylint: disable-msg=W0613
        """Checks whether the entity qualifies as a target for this action

        Args:
            entity: The entity to check.
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        return False
