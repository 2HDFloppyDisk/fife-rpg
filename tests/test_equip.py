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

from fife_rpg.components import equip, equipable

from bGrease.world import BaseWorld
from bGrease.entity import Entity

import unittest

class TestEquip(unittest.TestCase):
           
    class GameWorld(BaseWorld):
        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.equipable = equipable.Equipable()
            equipable.Equipable.registered_as = "equipable"
            self.components.equip = equip.Equip()
            equip.Equip.registered_as = "equip"

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.world = self.GameWorld()
        self.wearer = Entity(self.world)
        self.arms_item = Entity(self.world)
        self.arms_item.equipable.possible_slots = ["l_arm", "r_arm"]
        self.l_arm_item = Entity(self.world)
        self.l_arm_item.equipable.possible_slots = ["l_arm"]
        self.r_arm_item = Entity(self.world)
        self.r_arm_item.equipable.possible_slots = ["r_arm"]
        self.t_arm_item = Entity(self.world)
        self.t_arm_item.equipable.possible_slots = ["t_arm"]
        
    def test_equip_and_take(self):
        self.assertRaises(equip.SlotInvalidError, equip.equip, self.wearer, self.t_arm_item, "t_arm")
        self.assertRaises(equip.CannotBeEquippedInSlot, equip.equip, self.wearer, self.l_arm_item, "r_arm")
        equip.equip(self.wearer, self.l_arm_item, "l_arm")
        equip.equip(self.wearer, self.r_arm_item, "r_arm")
        self.assertIsNotNone(self.l_arm_item.equipable.wearer)
        self.assertRaises(equip.AlreadyEquippedError, equip.equip, self.wearer, self.l_arm_item, "r_arm")
        equip.equip(self.wearer, self.arms_item, "r_arm")
        self.assertIsNone(self.r_arm_item.equipable.wearer)
        self.assertIsNotNone(self.arms_item.equipable.wearer)
        equip.take_equipable( self.wearer, self.l_arm_item.equipable.in_slot)
        self.assertIsNone(self.l_arm_item.equipable.wearer)
        
    def tearDown(self):
        self.world = None
        self.wearer = None
        self.arms_item = None
        self.l_arm_item = None
        self.r_arm_item = None
        self.t_arm_item = None


