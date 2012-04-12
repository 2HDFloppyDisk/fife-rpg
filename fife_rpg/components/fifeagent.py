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

"""The FifeAgent component and functions

.. module:: fifeagent
    :synopsis: The FifeAgent component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base

class FifeAgent(Base): # pylint: disable-msg=R0904
    """Component that stores the values for a fife agent"""
    
    def __init__(self):
        """Constructor"""
        Base.__init__(self, layer=object, behaviour=object)

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        fields.remove("layer")
        fields.remove("behaviour")
        return fields

        
def setup_behaviour(agent):
    """Attach the behaviour to the layer
    
    Args;
        agent: A FifeAgent instance
    """
    if agent.behaviour:   
        agent.behaviour.attachToLayer(agent.entity.getID(), agent.layer)
        
def approach(agent, target_or_location, action):
    """Move the agent to the given location, or follow the given target while
    performing the given action

    Args:
        agent: A FifeAgent instance
        target_or_location: A location to move to or another agent to follow
        action: The name of the action to perform
    """
    if agent.behaviour: 
        agent.behaviour.approach(target_or_location, action)
        
COMMANDS = {"approach":approach}
