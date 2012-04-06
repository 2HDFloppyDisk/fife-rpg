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

# This is based on the PARPG components package

"""This contains the general components used by fife-rpg"""


from character_statistics import CharacterStatistics
from containable import Containable
from container import Container
from description import Description
from dialogue import Dialogue
from fifeagent import FifeAgent
from lockable import Lockable
from usable import Usable
from change_map import ChangeMap
from equipable import Equipable
from equip import Equip
from general import General
from behaviour import Behaviour
from graphics import Graphics

components = {
        "general": General(),
        "characterstats": CharacterStatistics(),
        "containable": Containable(),
        "container": Container(),
        "description": Description(),
        "dialogue": Dialogue(),
        "fifeagent": FifeAgent(),
        "lockable": Lockable(),
        "usable": Usable(),
        "change_map": ChangeMap(),
        "equipable": Equipable(),
        "equip": Equip(),
        "behaviour": Behaviour(),
        "graphics": Graphics(),
    }
