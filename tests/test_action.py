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
