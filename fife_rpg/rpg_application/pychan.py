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

"""This module contains the application class for pychan.

.. module:: pychan
    :synopsis: Contains the pychan application class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from __future__ import absolute_import
from __future__ import print_function
from fife import fife
from fife.extensions import pychan
from fife.extensions.pychan.pychanbasicapplication import PychanApplicationBase

from fife_rpg.rpg_application.base import RPGApplication
from fife_rpg.rpg_application.base import BaseEventListener
from fife_rpg.console_commands import get_commands


class PychanListener(BaseEventListener, fife.ConsoleExecuter):
    """Listener for pychan"""

    def __init__(self, app):
        BaseEventListener.__init__(self, app)
        fife.ConsoleExecuter.__init__(self)
        self.console = pychan.manager.hook.guimanager.getConsole()
        self.console.setConsoleExecuter(self)

    def keyPressed(self, evt):  # pylint: disable=W0221, C0103
        keyval = evt.getKey().getValue()
        if keyval == fife.Key.F10:
            pychan.manager.hook.guimanager.getConsole().toggleShowHide()
            evt.consume()
        else:
            BaseEventListener.keyPressed(self, evt)

    def onConsoleCommand(self, command):  # pylint: disable=C0103,W0221
        """Process console commands

        Args:
        command: A string containing the command

        Returns:
        A string representing the result of the command
        """
        result = ""

        args = command.split(" ")
        cmd = []
        for arg in args:
            arg = arg.strip()
            if arg != "":
                cmd.append(arg)

        if cmd[0].lower() in ('quit', 'exit'):
            self.app.quit()
            result = 'quitting'
        elif cmd[0] in get_commands():
            result = get_commands()[cmd[0]](self._application, *cmd[1:])
        else:
            result = 'Command Not Found...'

        return result

    def onToolsClick(self):  # pylint: disable=C0103,W0221
        """Gets called when the the 'tool' button on the console is clicked"""
        print("No tools set up yet")


class RPGApplicationPychan(RPGApplication, PychanApplicationBase):
    """The RPGApplication with fifechan support"""

    def __init__(self, setting=None):
        RPGApplication.__init__(self, setting)
        PychanApplicationBase.__init__(self, setting)

    def createListener(self):  # pylint: disable=C0103
        self._listener = PychanListener(self)
        return self._listener
