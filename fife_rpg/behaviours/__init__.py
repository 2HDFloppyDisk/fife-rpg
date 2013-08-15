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

#  This package is based on the entities package from PARPG

"""This package contains the behaviours

.. module:: behaviours
    :synopsis: Contains the behaviours

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.behaviours import behaviour_manager as BehaviourManager
from fife_rpg.helpers import Enum

AGENT_STATES = Enum(["NONE",
                     "IDLE",
                     "APPROACH",
                     "RUN",
                     "WALK",
                     "TALK"
                     ])
