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

from fife_rpg.actions import ActionManager
from fife_rpg.actions.base import Base

class TestAction(Base):

    def __init__(self, test_list, test_variable):#pylint: disable=W0231
        self.test_list = test_list
        self.test_variable = test_variable

    def execute(self):
        self.test_list.append(self.test_variable)

class ManagerTest(unittest.TestCase):
    """Test the action manager"""

    def setUp(self):
        self.reg_action_func = ActionManager.register_action
        self.reg_action_params = ("Test", TestAction)
        self.reg_command_func = ActionManager.register_command
        self.reg_command_params = ("Test", None)

    def tearDown(self):
        ActionManager.clear_actions()
        ActionManager.clear_commands()

    def test_actions_dictionary(self):
        test_actions = {}
        self.assertEqual(ActionManager.get_actions(), test_actions)
        self.reg_action_func(*self.reg_action_params)
        self.assertNotEqual(ActionManager.get_actions(), test_actions)
        test_actions["Test"] = TestAction
        self.assertEqual(ActionManager.get_actions(), test_actions)
        ActionManager.clear_actions()
        test_actions = {}
        self.assertEqual(ActionManager.get_actions(), test_actions)

    def test_register_action(self):
        self.reg_action_func(*self.reg_action_params)
        self.assertRaises(ActionManager.AlreadyRegisteredError,
                          self.reg_action_func,
                          *self.reg_action_params)

    def test_commands_dictionary(self):
        test_commands = {}
        self.assertEqual(ActionManager.get_commands(), test_commands)
        self.reg_command_func(*self.reg_command_params)
        self.assertNotEqual(ActionManager.get_commands(), test_commands)
        test_commands["Test"] = None
        self.assertEqual(ActionManager.get_commands(), test_commands)
        ActionManager.clear_commands()
        test_commands = {}
        self.assertEqual(ActionManager.get_commands(), test_commands)

    def test_register_command(self):
        self.reg_command_func(*self.reg_command_params)
        self.assertRaises(ActionManager.AlreadyRegisteredError,
                              self.reg_command_func,
                              *self.reg_command_params)
