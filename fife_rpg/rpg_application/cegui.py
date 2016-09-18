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

"""This module contains the application class for cegui.

.. module:: cegui
    :synopsis: Contains the cegui application class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import absolute_import
from fife.extensions.cegui.ceguibasicapplication import CEGUIApplicationBase
from fife_rpg.rpg_application.base import BaseEventListener
from fife_rpg.rpg_application.base import RPGApplication


class CEGUIListener(BaseEventListener):
    """Listener for CEGUI"""
    pass


class RPGApplicationCEGUI(RPGApplication, CEGUIApplicationBase):
    """The RPGApplication with CEGUI support"""

    def __init__(self, setting=None):
        RPGApplication.__init__(self, setting)
        CEGUIApplicationBase.__init__(self, setting)

    def createListener(self):  # pylint: disable=C0103
        self._listener = CEGUIListener(self)
        return self._listener
