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
#
# This package is based on the gamescene classes of PARPG

"""This module contains the generic controller and view to display a
fife_rpg map.

.. module:: controllers
    :synopsis: The generic controller and view to display a
fife_rpg map.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

from fife_rpg import ViewBase
from fife_rpg import ControllerBase

class GameSceneListener(fife.IMouseListener):
    """The game listener.

    Handle mouse events in relation
    with game process.
    """

    def __init__(self, engine, gamecontroller):
        """Constructor

        Args:
            engine: The FIFE engine
            gamecontroller: The GameSceneController
        """
        self.engine = engine
        self.gamecontroller = gamecontroller

        self.eventmanager = self.engine.getEventManager()
        fife.IMouseListener.__init__(self)

    def mousePressed(self, event): # pylint: disable-msg=C0103,W0221
        """Called when a mouse button was pressed.

        Args:
            event: The mouse event
        """
        pass

    def mouseMoved(self, event): # pylint: disable-msg=C0103,W0221
        """Called when the mouse was moved.

        Args:
            event: The mouse event
        """
        pass

    def mouseReleased(self, event): # pylint: disable-msg=C0103,W0221
        """Called when a mouse button was released.

        Args:
            event: The mouse event
        """
        pass

    def mouseDragged(self, event): # pylint: disable-msg=C0103,W0221
        """Called when the mouse is moved while a button is being pressed.

        Args:
            event: The mouse event
        """
        pass

class GameSceneView(ViewBase):
    """The view responsible for showing the in-game gui"""

    def __init__(self, application):
        """Constructor

        Args:
            application: A fife_rpg.RPGApplication instance
        """
        ViewBase.__init__(self, application)

class GameSceneController(ControllerBase):
    """Handles the input for a game scene"""

    def __init__(self, view, application):
        """Constructor

        Args:
            view: The GameSceneView
            application: The RPGApplication
        """
        ControllerBase.__init__(self, view, application)

    def pump(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        ControllerBase.pump(self, time_delta)

