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

"""Action that moves the camera to another position

.. module:: move_camera
    :synopsis: Moves the camera to another position

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife_rpg.actions.base import BaseAction

class MoveCamera(BaseAction):
    
    def __init__(self, application, position, commands = None):
        BaseAction.__init__(self, application, commands)
        self.position = position

    def execute(self):
        active_camera = self.application.current_map.camera
        location = active_camera.getLocation()
        coords = location.getMapCoordinates()
        coords.x = self.position[0]
        coords.y = self.position[1]
        location.setMapCoordinates(coords)
        active_camera.setLocation(location)
        BaseAction.execute(self)        

    @classmethod
    def register(cls, name="MoveCamera"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the action was registered, False if not.
        """
        return (super(MoveCamera, cls).register(name))