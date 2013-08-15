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

from fife_rpg.components import equip, equipable, general

from bGrease.world import BaseWorld
from fife_rpg.entities import RPGEntity

import unittest

class TestEquip(unittest.TestCase):

    class GameWorld(BaseWorld):
        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.general = general.General()
            general.General.registered_as = "general"
            self.components.equipable = equipable.Equipable()
            equipable.Equipable.registered_as = "equipable"
            self.components.equip = equip.RPGEquip()
            equip.RPGEquip.registered_as = "equip"
            equip.Equip.registered_as = "equip"

        def get_entity(self, identifier):
            """Returns the entity with the identifier

            Args:
                identifier: The identifier of the entity

            Returns:
                The entity with the identifier or None
            """
            extent = getattr(self[RPGEntity], "general")
            entities = extent.identifier == identifier
            if len(entities) > 0:
                return entities.pop()
            return None

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.world = self.GameWorld()
        self.wearer = RPGEntity(self.world, "wearer")
        self.arms_item = RPGEntity(self.world, "arms_item")
        self.arms_item.equipable.possible_slots = ["l_arm", "r_arm"]
        self.l_arm_item = RPGEntity(self.world, "l_arm_item")
        self.l_arm_item.equipable.possible_slots = ["l_arm"]
        self.r_arm_item = RPGEntity(self.world, "r_arm_item")
        self.r_arm_item.equipable.possible_slots = ["r_arm"]
        self.t_arm_item = RPGEntity(self.world, "t_arm_item")
        self.t_arm_item.equipable.possible_slots = ["t_arm"]
        self.two_hand_item = RPGEntity(self.world, "two_hand_item")
        self.two_hand_item.equipable.possible_slots = ["l_arm,r_arm", "head"]

    def test_equip_and_take(self):
        self.assertRaises(equip.SlotInvalidError, equip.equip,
                          self.wearer, self.t_arm_item, "t_arm")
        self.assertRaises(equip.CannotBeEquippedInSlot, equip.equip,
                          self.wearer, self.l_arm_item, "r_arm")
        equip.equip(self.wearer, self.l_arm_item, "l_arm")
        equip.equip(self.wearer, self.r_arm_item, "r_arm")
        self.assertIsNotNone(self.l_arm_item.equipable.wearer)
        self.assertRaises(equip.AlreadyEquippedError, equip.equip,
                          self.wearer, self.l_arm_item, "r_arm")
        equip.equip(self.wearer, self.arms_item, "r_arm")
        self.assertIsNone(self.r_arm_item.equipable.wearer)
        self.assertIsNotNone(self.arms_item.equipable.wearer)
        equip.take_equipable(self.wearer, self.l_arm_item.equipable.in_slot)
        self.assertIsNone(self.l_arm_item.equipable.wearer)
        equip.equip(self.wearer, self.l_arm_item, "l_arm")
        equip.equip(self.wearer, self.r_arm_item, "r_arm")
        equip.equip(self.wearer, self.two_hand_item, "l_arm")
        self.assertIsNotNone(self.two_hand_item.equipable.wearer)
        self.assertItemsEqual(self.two_hand_item.equipable.in_slot.split(","),
                             ["r_arm", "l_arm"])
        equip.equip(self.wearer, self.l_arm_item, "l_arm")
        self.assertIsNotNone(self.l_arm_item.equipable.wearer)
        self.assertIsNone(self.two_hand_item.equipable.wearer)
        self.assertEqual(self.two_hand_item.equipable.in_slot.split(","),
                         ['None'])
        equip.equip(self.wearer, self.two_hand_item, "head")
        self.assertIsNotNone(self.two_hand_item.equipable.wearer)

    def tearDown(self):
        self.world = None
        self.wearer = None
        self.arms_item = None
        self.l_arm_item = None
        self.r_arm_item = None
        self.t_arm_item = None


