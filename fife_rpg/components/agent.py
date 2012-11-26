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
from fife_rpg.exceptions import AlreadyRegisteredError

"""The Agent component and functions

.. module:: agent
    :synopsis: The Agent component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base
from fife_rpg.systems.scriptingsystem import ScriptingSystem

class Agent(Base):
    """Component that stores the general values of an agent
    
    Fields:
        gfx: The name of the graphical representation
        
        map: On what map the agent is
        
        type: The type of the agent. actor, ground_object or item
        
        position: The position of the agent as a 2 or 3 item list or tuple
        
        rotation: The rotation of the agent in degrees
        
        stack_position: The stackposition of the agent
        
        behaviour_type: The behaviour of the agent
        
        walk_speed: How fast the agent walks
        
        run_speed: How fast the agent runs
        
        knows: What the agent knows about
    """

    def __init__(self):
        Base.__init__(self, gfx=str, map=str, type=str, position=list,
                      rotation=int, stack_position=int, behaviour_type=str, 
                      walk_speed=float, run_speed=float, knows=set)
        self.fields["type"].default = lambda: "actor"
        self.fields["walk_speed"].default = lambda: 0.0
        self.fields["run_speed"].default = lambda: 0.0

    @classmethod
    def register(cls, name="agent", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Agent, cls).register(name, auto_register))


def knows(agent, knowledge):
    """Checks wheter the agent knows about something.
    
    Args:
        agent: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` that has a
        agent component.
        
        knowledge: A string containing the knowledge
        
    Returns:
        True: If the agent knows about the knowlegde
        
        False: If the agent does not know about the knowledge
    """
    agent_data = getattr(agent, Agent.registered_as)
    return knowledge in agent_data.knows

def add_knowledge(agent, knowledge):
    """Add a knowledge item to the agent
    
    Args:
        agent: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` that has a
        agent component.
        
        knowledge: A string containing the knowledge
    """
    agent_data = getattr(agent, Agent.registered_as)
    agent_data.knows.add(knowledge)
    
#Register conditions
try:
    ScriptingSystem.register_condition("Knows", 
                                       lambda application, agent_name, knowledge:
                                       knows(application.world.get_entity(
                                                    agent_name), 
                                             knowledge))
except AlreadyRegisteredError:
    pass
#Register console commands
try:
    from fife_rpg.console_commands import register_command
    register_command("AddKnowledge", lambda application, agent_name, knowledge:
                     add_knowledge(application.world.get_entity(agent_name), 
                                   knowledge))
except AlreadyRegisteredError:
    pass