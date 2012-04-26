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

"""The Behaviour component and functions

.. module:: behaviour
    :synopsis: The Behaviour component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base
from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg import BehaviourManager

class Behaviour(Base):
    """Component that stores the values of the behaviour"""

    __dependencies = [FifeAgent]

    def __init__(self):
        """Constructor"""
        Base.__init__(self, behaviour_type=str)
        self.behaviour_type = "Base"

    @classmethod
    def register(cls, name="behaviour"):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the component was registered, False if not.
        """

        return (super(Behaviour, cls).register(name))

    @classmethod
    def setup(cls, data, entity):
        """Sets up the entity dictionary by reading a data dictionary

        Args:
            data: A dictionary containg the base data
            entity: A dictionary that will be used to create the Entity

        Returns: The modified entity dictionary

        Raises:
            NotRegisteredError if the class is not registered
        """
        entity = super(Behaviour, cls).setup(data, entity)
        if not FifeAgent.registered_as in entity:
            entity[FifeAgent.registered_as] = {}
        behaviour = BehaviourManager.get_behaviour(data["behaviour_type"])()
        entity[FifeAgent.registered_as]["behaviour"] = behaviour
