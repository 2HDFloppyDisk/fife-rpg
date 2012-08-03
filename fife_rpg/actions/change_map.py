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

"""The change_map action switches to a different map

.. module:: change_map
    :synopsis: Switches to a different map
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.actions.base import Base
from fife_rpg.components.change_map import ChangeMap
from fife_rpg.components.agent import Agent

class ChangeMapAction(Base):
    """Switches to a different map and places the agent on the location"""

    dependencies = [ChangeMap, Agent]
        
    def execute(self):
        """Execute the action
        
        Raises:
            :class:`fife_rpg.exceptions.NoSuchCommandError`
            if a command is detected that is not registered.
        """
        change_map = getattr(self.target, ChangeMap.registered_as)
        agent = getattr(self.agent, Agent.registered_as)
        self.application.move_agent(self.agent, 
                                    position=change_map.target_position,
                                    new_map=change_map.target_map)
        try:            
            self.application.switch_map(agent.map)
        except AttributeError:
            pass
        Base.execute(self)
    
    @property
    def menu_text(self):
        """Returns the text that is to be displayed in menus"""
        return "Change Map"
        
    @classmethod
    def check_agent(cls, entity): #pylint: disable-msg=W0613
        """Checks whether the entity qualifies as an agent for this action
        
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
    def check_target(cls, entity): #pylint: disable-msg=W0613
        """Checks whether the entity qualifies as a target for this action
        
        Args:
            entity: The entity to ceck. 
            A :class:`fife_rpg.entities.rpg_entity.RPGEntity` instance.

        Returns: True if the entity qualifes. False otherwise
        """
        change_map = getattr(entity, ChangeMap.registered_as) 
        if change_map:
            return True
        return False

    @classmethod
    def register(cls, name="ChangeMap"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        super(ChangeMapAction, cls).register(name)