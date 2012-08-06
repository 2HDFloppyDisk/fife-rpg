# -*- coding: utf-8 -*-
"""The goal of fife-rpg is to create an rpg-framework using the FIFEngine
and bGrease. It will use the source of PARPG as a basis and build upon it.
"""

from fife_rpg.map import Map
from fife_rpg.map import NoSuchRegionError
from fife_rpg.mvc import ViewBase
from fife_rpg.mvc import ControllerBase
from fife_rpg.rpg_application import RPGApplication
from fife_rpg.world import RPGWorld
from fife_rpg.game_scene import GameSceneView
from fife_rpg.game_scene import GameSceneController
from fife_rpg.game_scene import GameSceneListener
from fife_rpg.dialogue import Dialogue
from fife_rpg.dialogue import DialogueController
from fife_rpg.sound_engine import SoundEngine