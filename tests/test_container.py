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

class  TestContainer(unittest.TestCase):
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
        
        def __init__(self, world, identifier, max_bulk, slots):
            """Constructor"""
            RPGEntity.__init__(self, world, identifier)
            self.container.children = slots
            self.container.max_bulk = max_bulk
                
    
    class Item(RPGEntity):
        def __init__(self, world, identifier, bulk):
            """Constructor"""
            RPGEntity.__init__(self, world, identifier)
            self.containable.bulk = bulk
        
    def setUp(self):
        unittest.TestCase.setUp(self)        
        self.world = self.GameWorld()
        slots_15 = list()
        slots_25 = list()
        for _ in xrange(3):
            slots_15.append(None)
        
        for _ in xrange(10):
            slots_25.append(None)

        self.inv_15 = self.Inventory(self.world, "inv_15", 15, slots_15)
        self.inv_25 = self.Inventory(self.world, "inv_25", 25, slots_25)
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
        self.inv_15 = None
        self.inv_25 = None
        self.world = None

    def test_State(self):
        for child in self.inv_15.container.children:
            self.assertIsNone(child)

        for child in self.inv_25.container.children:
            self.assertIsNone(child)            
        
    def test_PutTake(self):
        self.assertIsNone(container.get_item(self.inv_15, 0))
        
        container.put_item(self.inv_15, self.sword_1, 0)        
        self.assertIsNotNone(container.get_item(self.inv_15, 0))
        self.assertIsNotNone(self.sword_1.containable.container)        
        sword_1_container = self.world.get_entity(
                                self.sword_1.containable.container)
        self.assertListEqual(self.inv_15.container.children,
                    sword_1_container.container.children)
        self.assertEqual(container.get_item(self.inv_15, 0), 
                         self.sword_1)
        self.assertEqual(container.get_item(self.inv_15, 0).containable.slot, 
                         self.sword_1.containable.slot)
        
        container.take_item(self.inv_15, 0)
        self.assertIsNone(self.inv_15.container.children[0])
        self.assertIsNone(self.sword_1.containable.container)        
        
    def test_Swap(self):
        self.assertIsNone(self.inv_15.container.children[0])
        
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
        self.assertListEqual(self.inv_15.container.children,
                    dagger_1_container.container.children)
        self.assertEqual(container.get_item(self.inv_15, 0).containable.container,
                         self.dagger_1.containable.container)
        self.assertEqual(container.get_item(self.inv_15, 0).containable.slot,
                         self.dagger_1.containable.slot)
        
    def test_BulkSlots(self):
        container.put_item(self.inv_15, self.sword_1)
        container.put_item(self.inv_25, self.sword_2)
        self.assertEqual(container.get_total_bulk(self.inv_15), self.sword_1.containable.bulk)
        self.assertEqual(container.get_total_bulk(self.inv_25), self.sword_2.containable.bulk)
        
        container.put_item(self.inv_15, self.axe_1)
        container.put_item(self.inv_25, self.axe_2)
        self.assertEqual(container.get_total_bulk(self.inv_15), container.get_total_bulk(self.inv_25))
        
        self.assertRaises(container.BulkLimitError, container.put_item, self.inv_15, self.spear_1)
        container.put_item(self.inv_25, self.spear_2)

        container.put_item(self.inv_15, self.dagger_1)
        container.put_item(self.inv_25, self.dagger_2)
        self.assertNotEqual(container.get_total_bulk(self.inv_15), container.get_total_bulk(self.inv_25))

        self.assertRaises(container.NoFreeSlotError, container.put_item, self.inv_15, self.mace_1)
        container.put_item(self.inv_25, self.mace_2)
