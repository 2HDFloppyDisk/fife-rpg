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

"""This package contains the main application classes

.. module:: rpg_application
    :synopsis: Contains the main application classes

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.rpg_application.base import RPGApplication
from fife_rpg.rpg_application.base import BaseEventListener
from fife_rpg.rpg_application.base import KeyFilter
try:
    from fife_rpg.rpg_application.pychan import RPGApplicationPychan
    from fife_rpg.rpg_application.pychan import PychanListener
except ImportError:
    class RPGApplicationPychan(object):
        """Just a dummy class that raises an exception"""
        def __init__(self, settings):
            raise RuntimeError("FIFE was build with fifechan disabled. "
                               "Pychan applications will not work.")
try:
    from fife_rpg.rpg_application.cegui import RPGApplicationCEGUI
    from fife_rpg.rpg_application.cegui import CEGUIListener
except ImportError:
    class RPGApplicationCEGUI(object):
        """Just a dummy class that raises an exception"""
        def __init__(self, settings):
            raise RuntimeError("FIFE was build without CEGUI enabled. "
                               "CEGUI applications will not work.")
try:
    from fife_rpg.rpg_application.rocket import RPGApplicationRocket
    from fife_rpg.rpg_application.rocket import RocketListener
except ImportError:
    class RPGApplicationRocket(object):
        """Just a dummy class that raises an exception"""
        def __init__(self, settings):
            raise RuntimeError("FIFE was build without librocket enabled. "
                               "Rocket applications will not work.")

