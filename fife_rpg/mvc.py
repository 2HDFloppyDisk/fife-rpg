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

# The source of this file is based on the mvc classes from PARPG.

"""Contains classes for a Model-View-Controller system

.. module:: mvc
    :synopsis: Contains classes for a Model-View-Controller system

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from bGrease.grease_fife.mode import Mode

class ViewBase(object):
    """Base class for views"""

    def __init__(self, application):
        """Constructor

        Args:
            application: A fife_rpg.RPGApplication instance
        """
        self.application = application

class ControllerBase(Mode):
    """Base of Controllers"""

    def __init__(self, view, application):
        """Constructor

        Args:
            application: The application that created this controller
            view: The view that is used by this controller
        """
        Mode.__init__(self, application.engine)
        self.view = view
        self.application = application

    def pump(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        #TODO: List exceptions that maybe raised here if any
        Mode.pump(self, time_delta)
