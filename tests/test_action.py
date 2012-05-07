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

from fife_rpg.components import action as ActionManager

class TestAction(ActionManager.Action):

    def __init(self, test_list, test_variable):
        self.test_list = test_list
        self.test_variable = test_variable

    def execute(self):
        self.test_list.append(self.test_variable)

class ManagerTest(unittest.TestCase):
    """Test the action manager"""

    def setUp(self):
        self.reg_func = ActionManager.register_action
        self.reg_params = ("Test", TestAction)

    def tearDown(self):
        ActionManager.clear_actions()

    def test_actions_dictionary(self):
        test_actions = {}
        self.assertEqual(ActionManager.get_actions(), test_actions)
        self.reg_func(*self.reg_params)
        self.assertNotEqual(ActionManager.get_actions(), test_actions)
        test_actions["Test"] = TestAction
        self.assertEqual(ActionManager.get_actions(), test_actions)
        ActionManager.clear_actions()
        test_actions = {}
        self.assertEqual(ActionManager.get_actions(), test_actions)

    def test_register_action_not_present(self):
        self.reg_func(*self.reg_params)

    def test_register_action_already_present(self):
        self.reg_func(*self.reg_params)
        self.assertRaises(ActionManager.AlreadyRegisteredError,
                          self.reg_func,
                          *self.reg_params)
