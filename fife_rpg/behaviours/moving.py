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

#  This module is based on the behaviour package from PARPG

"""This module contains the basic behaviour for agents.

.. module:: base
    :synopsis: Contains the behaviour for agents that can move around on maps.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife import fife

from fife_rpg.behaviours import AGENT_STATES
from fife_rpg.behaviours.base import Base

class Moving(Base):
    """Behaviour that contains the methods for agents that can move around on
    maps.
    
    Properties:
        agent: A :class:`fife.Instance` that represents the agent.
        
        state: The current state of the behaviour.
        
        animation_queue: A deque that contains the queued animations.
        
        next_action: The :class:`fife_rpg.actions.base.Base` that will be 
        executed after the current animation is finished.
        
        registered_as: Class property that sets under what name the class is
        registered.
        
        dependencies: Class property that sets the classes this System depends
        on.

        walk_speed: How fast the agent will move when walking.
        
        run_speed: How fast the agent will move when running.
        
        walk_action: The name of the action that is played when the agent is
        walking. Defaults to "walk".
        
        run_action: The name of the action that is played when the agent is
        running. Defaults to "run".

    """

    def __init__(self, walk_speed, run_speed, walk_action="walk", 
                 run_action="run"):
        Base.__init__(self)
        self.walk_speed = walk_speed
        self.walk_action = walk_action
        self.run_speed = run_speed
        self.run_action = run_action

    @classmethod
    def register(cls, name="Moving"):
        """Registers the class as a Behaviour

        Args:
            name: The name under which the class should be registered
        Returns:
            True if the behaviour was registered, False if not.
        """
        return (super(Moving, cls).register(name))        

    def approach(self, location_or_agent, action=None):
        """Approaches a location or another agent and then perform an animation
        (if set).
        
        Args:
            loc: The location, as a tuple, or agent, as a 
            :class:`fife.Instance` to approach
            
            action: The :class:`fife_rpg.actions.base.Base` to schedule for 
            execution after the approach.
        """
            
        self.state = AGENT_STATES.APPROACH
        self.next_action = action
        if  isinstance(location_or_agent, fife.Instance):
            agent = location_or_agent
            self.agent.follow(self.run_action, agent, self.run_speed)
        else:
            location = location_or_agent
            boxLocation = tuple([int(float(i)) for i in location])
            location = fife.Location(self.getLocation())
            location.setLayerCoordinates(fife.ModelCoordinate(*boxLocation))
            self.agent.move(self.run_action, location, self.run_speed)   
        
    def run(self, location):
        """Makes the agent run to a certain location
        
        Args:
            location: Screen position to run to.
        """
        self.state = AGENT_STATES.RUN
        self.clear_animations()
        self.next_action = None
        self.agent.move(self.run_action, location, self.run_speed)

    def walk(self, location):
        """Makes the agent walk to a certain location.
        
        Args:
            location: Screen position to walk to.
        """
        self.state = AGENT_STATES.RUN
        self.clear_animations()
        self.next_action = None
        self.agent.move(self.walk_action, location, self.walk_speed)       
        