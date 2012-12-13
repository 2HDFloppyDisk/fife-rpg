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
from fife_rpg.components import character_statistics, general 
from fife_rpg.systems.character_statistics import CharacterStatisticSystem, getStatCost    
       
class TestStatistics(unittest.TestCase):
    
    class GameWorld(BaseWorld):
        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.char_stats = character_statistics.CharacterStatistics()
            character_statistics.CharacterStatistics.registered_as = "char_stats"
            self.components.general = general.General()
            self.systems.char_stats = CharacterStatisticSystem()
            CharacterStatisticSystem.registered_as = "char_stats"

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
    
    class Character(RPGEntity):
        """Entity representing a character"""
        
        def __init__(self, world, identifier):
            RPGEntity.__init__(self, world, identifier)
            self.char_stats.gender = "male" #Initialize the char_stats component

    def setUp(self):
        unittest.TestCase.setUp(self)        
        self.world = self.GameWorld()
        self.world.systems.char_stats.add_primary_statistic(
                "ST", "Strength", "Strength of the character")
        self.world.systems.char_stats.add_primary_statistic(
                "FT", "Fitness", "Fitness of the character")
        self.world.systems.char_stats.add_primary_statistic(
                "CO", "Coordination", "Coordination of the character")
        self.world.systems.char_stats.add_secondary_statistic(
                "LC", "Lifting capacity", "How much the character can lift",
                {"ST":0.7, "FT":0.3})
        self.world.systems.char_stats.add_secondary_statistic(
                "MD", "Melee Damage", "How much damage is done in melee",
                {"ST":0.7, "CO":0.3})
        self.world.systems.char_stats.add_secondary_statistic(
                "SPD", "Sprint Speed", "How fast the character can run",
                {"FT":0.7, "ST":0.3})
        self.character = self.Character(self.world, "Character") 
        self.character.char_stats.primary_stats["ST"] = 99
        self.character.char_stats.primary_stats["FT"] = 84
        self.character.char_stats.primary_stats["CO"] = 35
        self.world.systems.char_stats.step(0)
        
    def test_statistics(self):
        print "Test statistic calculation"
        char_stats = self.character.char_stats
        primary_stats = char_stats.primary_stats
        secondary_stats = char_stats.secondary_stats
        stat = secondary_stats["LC"]
        correct = 0.7 * primary_stats["ST"] + 0.3 * primary_stats["FT"]
        print "%d == %d ?" % (stat, correct)
        self.assertEqual(stat, correct, 
                         "Secondary statistics are not calculated correctly")
        
        stat = secondary_stats["MD"]
        correct = 0.7 * primary_stats["ST"] + 0.3 * primary_stats["CO"]
        print "%d == %d ?" % (stat, correct)
        self.assertEqual(stat, correct,
                         "Secondary statistics are not calculated correctly")
        
        stat = secondary_stats["SPD"]
        correct = 0.7 * primary_stats["FT"] + 0.3 * primary_stats["ST"]
        print "%d == %d ?" % (stat, correct)
        self.assertEqual(stat, correct, 
                         "Secondary statistics are not calculated correctly")

    def test_cost(self):    
        print "Test statistic cost/gain calculation"
        char_stats_system = self.world.systems.char_stats
        cost = char_stats_system.get_statistic_increase_cost(self.character, "ST")
        self.assertEqual(cost, 10, 
                "Character statistic increase cost is not calculated correctly")
        
        cost = char_stats_system.get_statistic_increase_cost(self.character, "FT")
        self.assertEqual(cost, 5, 
                "Character statistic increase cost is not calculated correctly")
        
        cost = char_stats_system.get_statistic_increase_cost(self.character, "CO")
        self.assertEqual(cost, 1, 
                "Character statistic increase cost is not calculated correctly")

        gain = char_stats_system.get_statistic_decrease_gain(self.character, "FT")
        self.assertEqual(gain, 4, 
                "Character statistic increase cost is not calculated correctly")
    
    def test_increase_decrease(self):
        print "Test increasing/decreasing statistics"
        char_stats_system = self.world.systems.char_stats
        char_stats = self.character.char_stats
        can_increase = char_stats_system.can_increase_statistic(self.character, 
                                                                "CO")
        self.assertFalse(can_increase, "Statistic should not be increasable")
        char_stats.stat_points = 1
        can_increase = char_stats_system.can_increase_statistic(self.character,
                                                                "CO")
        self.assertTrue(can_increase, "Statistic should be increasable")
        char_stats_system.increase_statistic(self.character,"CO")
        can_increase = char_stats_system.can_increase_statistic(self.character,
                                                                "CO")
        self.assertFalse(can_increase, "Statistic should not be increasable")
        
        can_increase = char_stats_system.can_increase_statistic(self.character,
                                                                "FT")
        self.assertFalse(can_increase, "Statistic should not be increasable")
        char_stats.stat_points = 5
        
        can_increase = char_stats_system.can_increase_statistic(self.character,
                                                                "FT")
        self.assertTrue(can_increase, "Statistic should be increasable")
        self.character.char_stats.primary_stats["CO"] = 1
        can_decrease = char_stats_system.can_decrease_statistic(self.character,
                                                                "CO")
        self.assertTrue(can_decrease, "Statistic should be decreasable")
        char_stats_system.decrease_statistic(self.character, "CO")          
        can_decrease = char_stats_system.can_decrease_statistic(self.character,
                                                                "CO")
        self.assertFalse(can_decrease, "Statistic should not be decreasable")         