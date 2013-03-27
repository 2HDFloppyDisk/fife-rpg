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

from fife.fife import DoubleRect, DoublePoint

from fife_rpg.map import Map, NoSuchRegionError

TEST_LAYER = "TestLayer"
# Dummy classes

class FifeCamera(object):
    """Dummy class that acts like a fife camera as needed"""
    
    def __init__(self):
        self.enabled = False
    
    def isEnabled(self):
        return self.enabled
    
    def setEnabled(self, value):
        self.enabled = value
        
class FifeLayer(object):
    """Dummy class that acts like a fife layer as needed"""
    
    def __init__(self, identifier):
        self.identifier = identifier

class FifeMap(object):
    """Dummy class that acts like a fife map as needed"""
    
    def __init__(self):
        self.camera = FifeCamera()
        self.layers = layers = {}
        layers[TEST_LAYER] = FifeLayer(TEST_LAYER)


    def getCamera(self, name=None):#pylint: disable=W0613
        #Being lazy here as this is not part of the actual test
        return self.camera
    
    def getLayer(self, name):#pylint: disable=W0613
        #Being lazy here as this is not part of the actual test
        return self.layers[name]

# Test cases

class Test(unittest.TestCase):


    def setUp(self):
        self.regions = {}
        self.regions["Alpha"] = DoubleRect(0, 0, 100, 100)
        self.regions["Beta"] = DoubleRect(300, 500, 200, 200)
        self.map_name = "Test"
        self.fife_map = FifeMap()
        self.fife_camera = self.fife_map.getCamera()
        self.test_layer = self.fife_map.getLayer(TEST_LAYER)

    def tearDown(self):
        pass


    def test_map(self):        
        rpg_map = Map(self.fife_map, self.map_name, "Default", self.regions)
        self.assertEqual(self.map_name, rpg_map.name, 
                         "Map.name does not return the correct value")
        self.assertEqual(self.fife_map, rpg_map.fife_map, 
                         "Map.map does not return the correct value")
        self.assertEqual(self.fife_camera, rpg_map.camera,
                         "Map.camera does not return the correct value")
        self.assertEqual(self.test_layer, rpg_map.get_layer(TEST_LAYER), 
                         "Map.get_layer does not return the correct value")
        self.assertDictEqual(self.regions, rpg_map.regions,
                         "Map.regions does not return the correct value")
        self.assertDictEqual({}, rpg_map.entities,
                             "Entities dictionary is not empty")
        self.assertFalse(rpg_map.is_active, 
                         "Map should not be active")
        rpg_map.activate()
        self.assertTrue(rpg_map.is_active, 
                        "Map should be active")
        rpg_map.deactivate()
        self.assertFalse(rpg_map.is_active, 
                         "Map should not be active")
        point = DoublePoint(50, 50)
        self.assertTrue(rpg_map.is_in_region(point, "Alpha"), 
                        "50, 50 should be in region Alpha")
        self.assertFalse(rpg_map.is_in_region(point, "Beta"), 
                        "50, 50 should not be in region Beta")
        self.assertRaises(NoSuchRegionError, 
                          rpg_map.is_in_region, point, "Gamma")
