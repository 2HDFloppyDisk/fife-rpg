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

# This package is based on the gamescene classes of PARPG

"""This module contains the generic controller and view to display a
fife_rpg map.

.. module:: controllers
    :synopsis: The generic controller and view to display a
fife_rpg map.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import os
from copy import deepcopy

from fife import fife
from fife.extensions.loaders import loadMapFile

from fife_rpg.exceptions import AlreadyRegisteredError
from fife_rpg import Map
from fife_rpg import ViewBase
from fife_rpg import ControllerBase
from fife_rpg import RPGWorld

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
    """The view responsible showing the in-game gui"""

    def __init__(self, engine, controller=None):
        """Constructor

        Args:
            engine: The FIFE engine
            controller: The GameSceneController
        """
        ViewBase.__init__(self, engine,  controller)

class GameSceneController(ControllerBase, RPGWorld):
    """Handles the input for a game scene"""

    def __init__(self,  view, application):
        """Constructor

        Args:
            view: The GameSceneView
            application: The RPGApplication
        """
        ControllerBase.__init__(self, view, application)
        RPGWorld.__init__(self, self.engine)
        self.__maps = {}
        self.__current_map = None

    @property
    def current_map(self):
        """Returns the current active map"""
        return self.__current_map

    @property
    def maps(self):
        """Returns a copy of the maps dictionary"""
        return deepcopy(self.__maps)

    def add_map(self, name, filename_or_map):
        """Adds a map to the maps dictionary.
        
        Args:
            name: The name of the map
            filename_or_map: The path to the map or a Map instance.
        """
        if not name in self.__maps:
            self.__maps[name] = filename_or_map
        else:
            raise AlreadyRegisteredError(name, "Map")

    def load_map(self, name):
        """Load the map with the given name

        Args:
            name: The name of the map to load
        """
        if name in self.__maps:
            game_map = self.__maps[name]
            if not isinstance(game_map, Map):
                use_lighting = self.application.settings.get(
                    "fife-rpg", "UseLighting", False)
                maps_path = self.application.settings.get(
                    "fife-rpg", "MapsPath", "maps")
                grid_type = self.application.settings.get(
                    "fife-rpg", "GridType", "square")
                grid_type = (self.application.engine.getModel().
                                getCellGrid(grid_type)
                             )
                camera = self.application.settings.get(
                    "fife-rpg", "Camera", "main")
                agent_layer = self.application.settings.get(
                "fife-rpg", "AgentLayer", "agents")
                fife_map = loadMapFile(os.path.join(
                                            maps_path, game_map + '.xml'),
                                       self.engine, extensions = {
                                            'lights': use_lighting})
                fife_map.createLayer(agent_layer, grid_type)
                #TODO: (Beliar) Add loading of additional objects, like regions
                #and entities
                regions = {}
                self.__maps[name] = Map(fife_map, name, camera, agent_layer,
                                        regions)
        else:
            LookupError("The map with the name '%s' cannot be found" %(name))
                
    def switch_map(self, name):
        '''Switches to the given map.

        Args:
            filename: The name of the map
        '''
        if name in self.__maps:
            self.load_map(name)
            if self.__current_map:
                self.__current_map.deactivate()
            self.__current_map = self.maps[name]
            self.__current_map.activate()
        else:
            LookupError("The map with the name '%s' cannot be found" 
                        %(name))

