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

"""This module contains the application class for librocket.

.. module:: rocket
    :synopsis: Contains the librocket application class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife import fife
from fife.extensions.librocket.rocketbasicapplication \
                                                import RocketApplicationBase

from fife_rpg.rpg_application.base import BaseEventListener


class RocketListener(BaseEventListener):
    """Listener for Rocket"""

    def __init__(self, app):
        BaseEventListener.__init__(self, app)
        self.debuggeractive = False

    def keyReleased(self, evt):  # pylint: disable-msg=C0103,W0221
        keyval = evt.getKey().getValue()

        if keyval == fife.Key.F12:
            if not self.debuggeractive:
                self.app.guimanager.showDebugger()
                self.debuggeractive = True
            else:
                self.app.guimanager.hideDebugger()
                self.debuggeractive = False
        else:
            BaseEventListener.keyReleased(self, evt)


class RPGApplicationRocket(RPGApplication, RocketApplicationBase):
    """THe RPGApplication with Rocket support"""

    def __init__(self, setting=None):
        RPGApplication.__init__(self, setting)
        RocketApplicationBase.__init__(self, setting)

    def createListener(self):  # pylint: disable-msg=C0103
        self._listener = RocketListener(self)
        return self._listener

