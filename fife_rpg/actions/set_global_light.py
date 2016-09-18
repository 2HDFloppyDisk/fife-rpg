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

"""Action that sets the light of the current map

.. module:: set_global_light
    :synopsis: Sets the light of the current map

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import absolute_import
from fife_rpg.actions.base import BaseAction


class SetGlobalLight(BaseAction):
    """Action that sets the values of the current maps light

    Properties:

        red: The red value of the light

        green: The green value of the light

        blue: The blue value of the light
    """

    def __init__(self, application, red, green, blue, commands=None):
        BaseAction.__init__(self, application, commands)
        self.red = red
        self.green = green
        self.blue = blue

    def execute(self):
        self.application.set_global_lighting(self.red,
                                             self.green,
                                             self.blue)
        BaseAction.execute(self)

    @classmethod
    def register(cls, name="SetGlobalLight"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return super(SetGlobalLight, cls).register(name)
