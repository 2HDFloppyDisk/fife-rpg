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

# The source of this file is based on the ViewBase class from PARPG.

"""This module contains the class that is the base for all views.

.. module:: view_base
    :synopsis: Contains the class that is the base for all views.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>

"""


class ViewBase(object):  # pylint: disable-msg=R0903
    """Base class for views"""

    def __init__(self, engine, controller=None):
        """Constructor

        Args:
            engine: A fife.Engine instance
            controller: A ControllerBase instance
                            that signifies the current controller of the View

        """
        self.engine = engine
        self.controller = controller
