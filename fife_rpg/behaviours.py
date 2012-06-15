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

"""This module manages the behaviours of fife-rpg agents.

.. module:: behaviours
    :synopsis: Manages the behaviours of fife-rpg agents.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from copy import copy
from collections import deque

from fife import fife

from fife_rpg.exceptions import AlreadyRegisteredError

(_AGENT_STATE_NONE, _AGENT_STATE_IDLE, _AGENT_STATE_APPROACH, _AGENT_STATE_RUN,
_AGENT_STATE_WANDER, _AGENT_STATE_TALK)= xrange(6)

class Behaviour (fife.InstanceActionListener):
    """Fife agent listener"""

    __registered_as = None

    def __init__(self):
        fife.InstanceActionListener.__init__(self)
        self.agent = None
        self.state = None
        self.animation_queue = deque()
        self.next_action = None

    @property
    def location(self):
        """Returns the location of the agent"""
        return self.agent.getLocation().getLayerCoordinates()
    
    @property
    def rotation(self):
        """Returns the rotation of the agent"""
        return self.agent.getRotation()
    
    @rotation.setter
    def rotation(self, rotation):
        """Sets the rotation of the agent"""
        self.agent.setRotation(rotation)
    
    def attach_to_layer(self, agent_id, layer):
        """Attaches to a certain layer

        Args:
           agent_id: ID of the layer to attach to.
           layer: Layer of the agent to attach the behaviour to
        """
        self.agent = layer.getInstance(agent_id)
        self.agent.addActionListener(self)
        self.state = _AGENT_STATE_NONE

    def on_new_map(self, layer):
        """Called when the agent is moved to a different map

        Args:
            layer: The layer that the agent was moved to
        """
        if self.agent is not None:
            self.agent.removeActionListener(self)

        self.agent = layer.getInstance(self.parent.general.identifier)
        self.agent.addActionListener(self)
        self.state = _AGENT_STATE_NONE

    def idle(self):
        """Set the state to idle"""
        self.state = _AGENT_STATE_IDLE

    def onInstanceActionFinished(self, instance, action):
        #pylint: disable=C0103,W0613,W0221
        """Called by FIFE when an action of an agent is finished

        Args:
            instance: The agent instance
            action: The action that the agent was doing
        """
        # First we reset the next behavior 
        act = self.next_action
        self.next_action = None 
        self.idle()

        if act:
            act.execute()
        try:
            animtion = self.animation_queue.popleft()
            self.animate(**animtion)
        except IndexError:
            self.idle()

    def onInstanceActionFrame(self, instance, action, frame):
        #pylint: disable=C0103,W0613,W0221
        """Called by FIFE when a frame of an action of an agent is finished

        Args:
            instance: The agent instance
            action: The action that the agent was doing
            frame: The frame that the was done
        """
        pass

    def talk(self):
        """Set the agent to their talking animation"""
        self.state = _AGENT_STATE_TALK
        self.clear_animations()
        self.idle()

    def animate(self, action, direction = None, repeating = False):
        """Perform an animation

        Args:
            action: The action to perform
            direction: The direction to which the agent should face
            repeating: Whether to repeat the action or not
        """
        direction = direction or self.agent.getFacingLocation()
        self.agent.act(action, direction, repeating)

    def queue_animation(self, action, direction = None, repeating = False):
        """Add an action to the queue

        Args:
            action: The action to perform
            direction: The direction to which the agent should face
            repeating: Whether to repeat the action or not
        """
        self.animation_queue.append({"action": action, "direction": direction,
                                  "repeating": repeating})
        
    def clear_animations(self):
        """Remove all actions from the queue"""
        self.animation_queue.clear()

    @classmethod
    def register(cls, name="Base"):
        """Registers the class as a behaviour

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the behaviour was registered, False if not.
        """
        try:
            register_behaviour(name, cls)
            cls.__registered_as = name
            return True
        except AlreadyRegisteredError as error:
            print error
            return False

_BEHAVIOURS = {}

def register_behaviour(name, behaviour):
    """Registers a behaviour

    Args:
        name: The name of the behaviour
        behaviour: The behaviour class

    Raises:
        AlreadyRegisteredError if there is already a behaviour with that name
    """
    if name in _BEHAVIOURS:
        raise AlreadyRegisteredError("behaviour", name)
    else:
        _BEHAVIOURS[name] = behaviour

def get_behaviours():
    """Returns a copy of the behaviour dictionary"""
    return copy(_BEHAVIOURS)

def get_behaviour(name):
    """Returns the behaviour with the given name"""
    if name in _BEHAVIOURS:
        return _BEHAVIOURS[name]
    return None
