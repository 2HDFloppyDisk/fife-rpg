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
:class:`fife_rpg.map.GameMap`.

.. module:: game_scene
    :synopsis: The generic controller and view to display a fife_rpg map.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

from fife_rpg import ViewBase
from fife_rpg import ControllerBase

class GameSceneListener(fife.IMouseListener):
    """The game listener.

    Handle mouse events in relation
    with game process.

    Properties:
        engine: The FIFE engine

        gamecontroller: A :class:`fife_rpg.game_scene.GameSceneController`
        
        eventmanager: The engines eventmanager. A :class:`fife.EventManager`
    """

    def __init__(self, engine, gamecontroller):
        self.engine = engine
        self.gamecontroller = gamecontroller

        self.eventmanager = self.engine.getEventManager()
        fife.IMouseListener.__init__(self)
        
    def activate(self):
        """Makes the listener receive events"""
        self.eventmanager.addMouseListener(self)

    def deactivate(self):
        """Makes the listener receive events"""
        self.eventmanager.removeMouseListener(self)


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
    """The view responsible for showing the in-game gui

    Properties:
        application: A :class:`fife_rpg.rpg_application.RPGApplication` instance
    """

    def __init__(self, application):
        ViewBase.__init__(self, application)

class GameSceneController(ControllerBase):
    """Handles the input for a game scene

    Properties:
        view: A :class:`fife_rpg.game_scene.GameSceneView`
        
        application: A :class:`fife_rpg.rpg_application.RPGApplication`
        
        listener: The listener used by the game scene
    """

    def __init__(self, view, application, listener=None):
        ControllerBase.__init__(self, view, application)
        self.listener = listener or GameSceneListener(application.engine,
                                                      self)

    def on_activate(self):
        """Being called when the Mode is activated"""
        self.listener.activate()

    def on_deactivate(self):
        """Being called when the Mode is deactivated"""
        self.listener.deactivate()

    def pump(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        ControllerBase.pump(self, time_delta)

