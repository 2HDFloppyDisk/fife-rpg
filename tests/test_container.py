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

import unittest

from bGrease.world import BaseWorld

from fife_rpg.entities import RPGEntity
from fife_rpg.components import containable, container, general


class TestContainer(unittest.TestCase):

    class GameWorld(BaseWorld):

        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.general = general.General()
            general.General.registered_as = "general"
            self.components.containable = containable.Containable()
            containable.Containable.registered_as = "containable"
            self.components.container = container.Container()
            container.Container.registered_as = "container"

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

    class Inventory(RPGEntity):

        """Enity representing an Iventory"""

        def __init__(self, world, identifier, max_bulk, max_slots):
            RPGEntity.__init__(self, world, identifier)
            self.container.max_bulk = max_bulk
            self.container.max_slots = max_slots

    class Item(RPGEntity):

        def __init__(self, world, identifier, bulk, max_stack=1,
                     start_stack=1, item_type=""):
            RPGEntity.__init__(self, world, identifier)
            self.containable.bulk = bulk
            self.containable.max_stack = max_stack
            self.containable.current_stack = start_stack
            self.containable.item_type = item_type

    def reset_gold(self):
        self.gold_1 = self.Item(self.world, "gold_1", 0.25, 100, 20, "Gold")
        self.gold_2 = self.Item(self.world, "gold_2", 0.25, 100, 60, "Gold")
        self.gold_3 = self.Item(self.world, "gold_3", 0.25, 100, 30, "Gold")
        self.gold_4 = self.Item(self.world, "gold_4", 0.25, 100, 70, "Gold")
        self.gold_5 = self.Item(self.world, "gold_5", 0.25, 100, 40, "Gold")

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.world = self.GameWorld()

        self.inv_no_slots = self.Inventory(self.world, "inv_no_slots", 200,  0)
        self.inv_15 = self.Inventory(self.world, "inv_15", 15, 3)
        self.inv_25 = self.Inventory(self.world, "inv_25", 25, 10)
        self.dagger_1 = self.Item(self.world, "dagger_1", 2)
        self.sword_1 = self.Item(self.world, "sword_1", 4)
        self.axe_1 = self.Item(self.world, "axe_1", 4)
        self.mace_1 = self.Item(self.world, "mace_1", 5)
        self.spear_1 = self.Item(self.world, "spear_1", 8)
        self.dagger_2 = self.Item(self.world, "dagger_2", 2)
        self.sword_2 = self.Item(self.world, "sword_2", 4)
        self.axe_2 = self.Item(self.world, "axe_2", 4)
        self.mace_2 = self.Item(self.world, "mace_2", 5)
        self.spear_2 = self.Item(self.world, "spear_2", 8)
        self.paper_1 = self.Item(self.world, "paper_1", 0.1, 20, 5, "Paper")
        self.gold_1 = None
        self.gold_2 = None
        self.gold_3 = None
        self.gold_4 = None
        self.gold_5 = None
        self.reset_gold()
        self.small_purse = self.Item(self.world, "small_purse", 0.25, 1, 0,
                                     "Gold")

    def tearDown(self):
        self.dagger_1 = None
        self.sword_1 = None
        self.axe_1 = None
        self.mace_1 = None
        self.spear_1 = None
        self.dagger_2 = None
        self.sword_2 = None
        self.axe_2 = None
        self.mace_2 = None
        self.spear_2 = None
        self.paper_1 = None
        self.gold_1 = None
        self.gold_2 = None
        self.gold_3 = None
        self.gold_4 = None
        self.gold_5 = None
        self.small_purse = None
        self.inv_15 = None
        self.inv_25 = None
        self.inv_no_slots = None
        self.world = None

    def test_PutTakeSlots(self):
        self.assertIsNone(container.get_item(self.inv_15, 0))

        container.put_item(self.inv_15, self.sword_1, 0)
        self.assertIsNotNone(container.get_item(self.inv_15, 0))
        self.assertIsNotNone(self.sword_1.containable.container)
        sword_1_container = self.world.get_entity(
            self.sword_1.containable.container)
        self.assertListEqual(container.get_items(self.inv_15),
                             container.get_items(sword_1_container))
        self.assertEqual(container.get_item(self.inv_15, 0),
                         self.sword_1)
        self.assertEqual(container.get_item(self.inv_15, 0).containable.slot,
                         self.sword_1.containable.slot)

        container.take_item(self.inv_15, 0)
        self.assertIsNone(container.get_item(self.inv_15, 0))
        self.assertIsNone(self.sword_1.containable.container)

    def test_PutTakeNoSlots(self):
        self.assertIsNone(container.get_item(self.inv_no_slots, 0))

        container.put_item(self.inv_no_slots, self.sword_1)
        self.assertIsNotNone(container.get_item(self.inv_no_slots,
                                                self.sword_1.containable.slot))
        self.assertIsNotNone(self.sword_1.containable.container)
        sword_1_container = self.world.get_entity(
            self.sword_1.containable.container)
        self.assertListEqual(container.get_items(self.inv_no_slots),
                             container.get_items(sword_1_container))
        self.assertEqual(container.get_item(self.inv_no_slots, 0),
                         self.sword_1)
        container.put_item(self.inv_no_slots, self.axe_2)
        self.assertEqual(self.axe_2.containable.slot, 1)
        container.put_item(self.inv_no_slots, self.mace_1, 5)
        self.assertEqual(self.mace_1.containable.slot, 2)
        self.assertEqual(container.take_item(self.inv_no_slots, 1), self.axe_2)
        self.assertEqual(self.mace_1.containable.slot, 1)
        self.assertEqual(container.take_item(self.inv_no_slots, 1),
                         self.mace_1)
        container.take_item(self.inv_no_slots, 1)
        temp_item = container.get_item(self.inv_no_slots, 0)
        self.assertEqual(temp_item.containable.slot,
                         self.sword_1.containable.slot)

        container.take_item(self.inv_no_slots, 0)
        self.assertIsNone(container.get_item(self.inv_no_slots, 0))
        self.assertIsNone(self.sword_1.containable.container)

    def test_Swap(self):
        self.assertIsNone(container.get_item(self.inv_15, 0))

        container.put_item(self.inv_15, self.sword_1, 0)
        sword1 = container.get_item(self.inv_15, 0)
        sword1_data = sword1.containable
        self.assertEqual(sword1_data.container,
                         self.sword_1.containable.container)
        self.assertEqual(sword1_data.slot, self.sword_1.containable.slot)

        sword2 = container.put_item(self.inv_15, self.dagger_1, 0)
        sword2_data = sword2.containable
        self.assertEqual(sword2_data.container, sword2_data.container)
        self.assertEqual(sword2_data.slot, sword2_data.slot)

        self.assertIsNotNone(container.get_item(self.inv_15, 0))
        dagger_1_container = self.world.get_entity(
            self.dagger_1.containable.container)
        self.assertListEqual(container.get_items(self.inv_15),
                             container.get_items(dagger_1_container))
        self.assertEqual(
            container.get_item(self.inv_15, 0).containable.container,
            self.dagger_1.containable.container)
        self.assertEqual(container.get_item(self.inv_15, 0).containable.slot,
                         self.dagger_1.containable.slot)

    def test_BulkSlots(self):
        container.put_item(self.inv_15, self.sword_1)
        container.put_item(self.inv_25, self.sword_2)
        self.assertEqual(container.get_total_bulk(self.inv_15),
                         self.sword_1.containable.bulk)
        self.assertEqual(container.get_total_bulk(self.inv_25),
                         self.sword_2.containable.bulk)

        container.put_item(self.inv_15, self.axe_1)
        container.put_item(self.inv_25, self.axe_2)
        self.assertEqual(container.get_total_bulk(self.inv_15),
                         container.get_total_bulk(self.inv_25))

        self.assertRaises(container.BulkLimitError, container.put_item,
                          self.inv_15, self.spear_1)
        container.put_item(self.inv_25, self.spear_2)

        container.put_item(self.inv_15, self.dagger_1)
        container.put_item(self.inv_25, self.dagger_2)
        self.assertNotEqual(container.get_total_bulk(self.inv_15),
                            container.get_total_bulk(self.inv_25))

        self.assertRaises(container.NoFreeSlotError, container.put_item,
                          self.inv_15, self.mace_1)
        container.put_item(self.inv_25, self.mace_2)

    def test_Stack(self):
        self.assertIsNone(container.get_item(self.inv_15, 0))
        container.put_item(self.inv_15, self.gold_1)
        self.assertIsNotNone(container.get_item(self.inv_15, 0))
        self.assertIsNotNone(self.gold_1.containable.container)
        self.assertRaises(container.BulkLimitError, container.put_item,
                          self.inv_15, self.gold_2)
        self.assertEqual(self.gold_1.containable.current_stack,
                         60)
        self.assertEqual(self.gold_2.containable.current_stack, 20)

        self.assertIsNone(container.get_item(self.inv_25, 0))
        container.put_item(self.inv_25, self.gold_3)
        container.put_item(self.inv_25, self.gold_4)
        self.assertEqual(self.gold_3.containable.current_stack, 100)
        self.assertEqual(self.gold_4.containable.current_stack, 0)

        self.reset_gold()

        # Testing if stacks are filled and a the rest put into a new slot
        self.assertIsNone(container.get_item(self.inv_no_slots, 0))
        container.put_item(self.inv_no_slots, self.gold_1)
        container.put_item(self.inv_no_slots, self.gold_4)
        self.assertEqual(self.gold_1.containable.current_stack, 90)
        self.assertEqual(self.gold_4.containable.current_stack, 0)
        container.put_item(self.inv_no_slots, self.gold_2)
        self.assertEqual(self.gold_1.containable.current_stack, 100)
        self.assertEqual(self.gold_2.containable.current_stack, 50)
        self.assertEqual(self.gold_1.containable.slot, 0)
        self.assertEqual(self.gold_2.containable.slot, 1)
        container.put_item(self.inv_no_slots, self.gold_3)
        self.assertEqual(self.gold_2.containable.current_stack, 80)
        self.assertEqual(self.gold_3.containable.current_stack, 0)
        container.put_item(self.inv_no_slots, self.gold_5)
        self.assertEqual(self.gold_2.containable.current_stack, 100)
        self.assertEqual(self.gold_5.containable.current_stack, 20)
        self.assertEqual(self.gold_1.containable.slot, 0)
        self.assertEqual(self.gold_2.containable.slot, 1)
        self.assertEqual(self.gold_5.containable.slot, 2)

    def test_StackSlotBulk(self):
        self.assertIsNone(container.get_item(self.inv_15, 0))
        container.put_item(self.inv_15, self.gold_1, 0)
        self.assertIsNotNone(container.get_item(self.inv_15, 0))
        self.assertIsNotNone(self.gold_1.containable.container)
        self.assertRaises(container.BulkLimitError, container.put_item,
                          self.inv_15, self.gold_2, 1)
        self.assertEqual(self.gold_1.containable.current_stack,
                         20)
        self.assertEqual(self.gold_2.containable.current_stack, 60)

    def test_StackSlotMerge(self):
        self.assertIsNone(container.get_item(self.inv_25, 0))
        container.put_item(self.inv_25, self.sword_1, 0)
        temp_item = container.put_item(self.inv_25, self.paper_1, 0)
        self.assertEqual(temp_item, self.sword_1)
        temp_item = container.put_item(self.inv_25, self.gold_1, 0)
        self.assertEqual(temp_item, self.paper_1)
        self.assertEqual(self.gold_1.containable.slot,
                         0)
        container.put_item(self.inv_25, self.gold_3, 1)
        self.assertEqual(self.gold_3.containable.slot, 1)
        container.put_item(self.inv_25, self.gold_5, 1)
        self.assertEqual(self.gold_1.containable.current_stack, 20)
        self.assertEqual(self.gold_3.containable.current_stack, 70)
        self.assertEqual(self.gold_5.containable.current_stack, 0)
        self.assertRaises(container.BulkLimitError, container.put_item,
                          self.inv_25, self.gold_2, 1)
        self.assertEqual(self.gold_3.containable.current_stack, 80)
        self.assertEqual(self.gold_2.containable.current_stack, 50)
