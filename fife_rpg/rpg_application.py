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

"""This module contains the main application class.

.. module:: rpg_application
    :synopsis: Contains the main application class.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import time

from bGrease.grease_fife.mode import FifeManager

from fife import fife
from fife.extensions.basicapplication import ApplicationBase
from fife.extensions.pychan.internal import get_manager

class KeyFilter(fife.IKeyFilter):
    """This is the implementation of the fife.IKeyFilter class.

    Prevents any filtered keys from being consumed by guichan.
    """

    def __init__(self, keys):
        """Sets up the keys to be filtered

        Args:
                keys: A list of fife.Key
        """
        fife.IKeyFilter.__init__(self)
        self._keys = keys
    
    def is_filtered(self, event):
        """Checks whether the key is filtered or not.

        Args:
            event: A fife.KeyEvent instance

        Returns:
            True if the key is filtered, False if not.
        """
        #TODO: List exceptions that maybe raised here if any
        return event.getKey().getValue() in self._keys


class ApplicationListener(
    fife.IKeyListener, fife.ICommandListener, fife.ConsoleExecuter):
    """A basic listener for window commands, console commands and keyboard
    inputs.

    Does not process game related input.
    """

    def __init__(self, engine, application):
        """Initializes all listeners and registers itself with the
        eventmanager.

        Args:
            engine: A fife.Engine instance
            application: A RPGApplication instance
        """
        #TODO: List exceptions that maybe raised here if any
        self._engine = engine
        self._application = application
        self._eventmanager = self._engine.getEventManager()

        fife.IKeyListener.__init__(self)
        self._eventmanager.addKeyListener(self)

        fife.ICommandListener.__init__(self)
        self._eventmanager.addCommandListener(self)

        fife.ConsoleExecuter.__init__(self)
        get_manager().getConsole().setConsoleExecuter(self)

        keyfilter = KeyFilter([fife.Key.ESCAPE, fife.Key.BACKQUOTE,
                               fife.Key.PRINT_SCREEN])
        keyfilter.__disown__()

        self._eventmanager.setKeyFilter(keyfilter)

        self.quit = False

    def keyPressed(self, event): # pylint: disable-msg=C0103,W0221
        """Processes any non game related keyboard input.

        Args:
            event: The fife.KeyEvent that happened
        """
        #TODO: List exceptions that maybe raised here if any
        if event.isConsumed():
            return

        keyval = event.getKey().getValue()

        if keyval == fife.Key.ESCAPE:
            self.quit = True
            event.consume()
        elif keyval == fife.Key.BACKQUOTE:
            get_manager().getConsole().toggleShowHide()
            event.consume()
        elif keyval == fife.Key.PRINT_SCREEN:
            self._engine.getRenderBackend().captureScreen(
                time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".png")
            event.consume()

    def keyReleased(self, event): # pylint: disable-msg=C0103,W0221
        """Gets called when a key is released

        Args:
            event: The fife.KeyEvent that happened
        """
        pass

    def onCommand(self, command): # pylint: disable-msg=C0103,W0221
        """Process commands

        Args:
            command: The fife.Command that is being processed
        """
        #TODO: List exceptions that maybe raised here if any
        self.quit = (command.getCommandType() == fife.CMD_QUIT_GAME)
        if self.quit:
            command.consume()

    def onConsoleCommand(self, command): # pylint: disable-msg=C0103,W0221
        """Process console commands

        Args:
            command: A string containing the command

        Returns:
            A string representing the result of the command
        """
        #TODO: List exceptions that maybe raised here if any
        result = ""

        args = command.split(" ")
        cmd = []
        for arg in args:
            arg = arg.strip()
            if arg != "":
                cmd.append(arg)

        if cmd[0].lower() in ('quit', 'exit'):
            self.quit = True
            result = 'quitting'
        elif cmd[0].lower() in ('help'):
            helptextfile = self._application.settings.get(
                "RPG", "HelpText", "misc/help.txt")
            get_manager().getConsole().println(open(helptextfile, 'r').read())
            result = "--OK--"
        elif cmd[0].lower() in ('eval'):
            try:
                result = str(eval(command.lstrip(cmd[0])))
            except: # pylint: disable-msg=W0702
                result = "Invalid eval statement..."
        else:
            result = self._application.onConsoleCommand(command)

        if not result:
            result = 'Command Not Found...'

        return result

    def onToolsClick(self): # pylint: disable-msg=C0103,W0221
        """Gets called when the the 'tool' button on the console is clicked"""
        print "No tools set up yet"


class RPGApplication(ApplicationBase,  FifeManager):
    """The main application.  It inherits fife.extensions.ApplicationBase."""

    def __init__(self, TDS):
        ApplicationBase.__init__(self,  TDS)
        FifeManager.__init__(self)
        self._listener = None

    @property
    def settings(self):
        """Returns the settings of the application.
        
        Returns:
            A fife_settings.Setting instance that contains the settings of the
            application.
        """
        return self._setting
    
    @property
    def log_manager(self):
        """Returns the log manager of the application.
        
        Returns:
            a fifelog.LogManager instance that contains the log manager of
            the application.
        """
        return self._log

    def createListener(self): # pylint: disable-msg=C0103
        """Creates the listener for the application."""
        self._listener = ApplicationListener(self.engine,  self)
        return self._listener

    def request_quit(self):
        """Sends the quit command to the application's listener.

        We could set self.quitRequested to true also but this is a
        good example on how to build and dispatch a fife.Command.
        """
        cmd = fife.Command()
        cmd.setSource(None)
        cmd.setCommandType(fife.CMD_QUIT_GAME)
        self.engine.getEventManager().dispatchCommand(cmd)

    def _pump(self):
        """Performs actions every frame."""
        if self._listener.quit:
            self.quit()
        else:
            FifeManager._pump(self)
