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

# The source of this file is based on the ControllerBase class from PARPG.

"""This module contains the class that is the base for all controllers.

.. module:: controller_base
    :synopsis: Contains the class that is the base for all controllers.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>

"""

from bGrease.grease_fife.mode import Mode


class ControllerBase(Mode):
    """Base of Controllers"""

    def __init__(self, view, application):
        """Constructor

        Args:
            application: The application that created this controller
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
