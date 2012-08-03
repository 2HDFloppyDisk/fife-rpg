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

#  This module is based on the scriptingsystem module from PARPG

"""The scripting system manages the scripts of fife-rpg games.

.. module:: scriptingsystem
    :synopsis: Manages the scripts of fife-rpg games.
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from collections import deque
from copy import copy

from fife_rpg.systems import Base
from fife_rpg.systems import GameEnvironment

class Script(object):
    """Script object
    
    Properties:
        actions: The actions that the script will run
        
        system: The Scriptsystem that this script will run on
        
        running_actions: The actions that are currently running
        
        running: Whether the script is currently running or not
        
        finished: Whether the script has finished running or not
        
        wait: The seconds that have to pass before the next action is run.
        
        cur_action: The current running action     
    """

    def __init__(self, actions, system):
        assert(isinstance(actions, deque))
        self.actions = actions
        assert(isinstance(system, ScriptingSystem))
        self.system = system
        self.running_actions = None
        self.running = False
        self.finished = False
        self._time = 0
        self.wait = 0
        self.cur_action = None
        self.reset()

    def reset(self):
        """Resets the state of the script"""
        self.running_actions = copy(self.actions)
        self.running = False
        self.finished = False
        self._time = 0
        self.wait = 0
        self.cur_action = None
    
    def update(self, time):
        """Advance the script
        
        Args:
            time: The time to advance the script by
        """
        if not self.running:
            return
        if self.cur_action and not self.cur_action.executed:
            return
        self._time += time
        if self.wait <= self._time:
            self._time = 0
            try:
                script_vals = self.system.getScriptEnvironment()
                action_data = self.running_actions.popleft()
                action = self.system.actions[action_data[0]]
                action_params = eval(
                                     action_data[1], 
                                     script_vals[0], script_vals[1]
                                     ) 
                if not (isinstance(action_params, list) 
                        or isinstance(action_params, tuple)):
                    action_params = [action_params]
                self.cur_action = action(self.system.world.application,
                                         *action_params)
                self.wait = action_data[2]
                if len(action_data) >= 4:
                    vals = (
                        eval(action_data[4], script_vals[0], script_vals[1]) 
                        if len(action_data) > 4
                        else ()
                    )
                    command = action_data[3]
                    self.system.commands[command](
                        *vals, 
                        action=self.cur_action
                    )
                else:
                    self.cur_action.execute()
            except IndexError:
                self.finished = True
                self.running = False


class ScriptingSystem(Base):
    """System responsible for managing scripts.
    
    Properties:
        commands: The commands available to scripts
        
        actions: Actions that the scripts can do
        
        scripts: Dictionary of the registered scripts
        
        conditions: List of the registered conditions
    """

    dependencies = [GameEnvironment]

    @classmethod
    def register(cls, name="scripting", *args, **kwargs):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered
            
            args: Additional arguments to pass to the class constructor
            
            kwargs: Additional keyword arguments to pass to the class 
            constructor

        Returns:
            True if the system was registered, False if not.
        """
        (super(ScriptingSystem, cls).register(name, **kwargs))
    
    def __init__(self, commands, actions):
        Base.__init__(self)
        self.commands = commands
        self.actions = actions
        self.scripts = {}
        self.conditions = []
        self.reset()

    def reset(self):
        """Resets the script and condition collections"""
        self.scripts = {}
        self.conditions = []

    def getScriptEnvironment(self):
        """Returns the environment that the scripts are running on"""
        environment = getattr(self.world.systems, 
                              GameEnvironment.registered_as)
        return environment.get_environement()

    def step(self, time_delta):
        """Execute a _time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time since last step invocation
        """
        for condition_data in self.conditions:
            condition = condition_data[0]
            script_name = condition_data[1]
            if not self.scripts.has_key(script_name):
                return
            script = self.scripts[script_name]
            if (eval(condition, *self.getScriptEnvironment()) 
                and not script.running):
                script.running = True
        for script in self.scripts.itervalues():
            assert(isinstance(script, Script))
            if script.finished:
                script.reset()
            elif script.running:
                script.update(time_delta)
                
    def set_script(self, name, actions):
        """Sets a script.

        Args:
            name: The name of the script
            
            actions: What the script does
        """
        if not(isinstance(actions, deque)):
            actions = deque(actions)
        self.scripts[name] = Script(actions, 
                                    self
                                    )
        
    def add_condition(self, condition, script_name):
        """Adds a condition.

        Args:
            condition: Condition which will be evaluated
            
            script_name: Name of the script that will be executed if the
            condition evaluates to True.
        """
        self.conditions.append((condition, script_name))
    
    
    def run_script(self, name):
        """Runs a script with the given name

        Args:
            name: The name of the script
        """
        if self.scripts.has_key(name):
            self.scripts[name].running = True
        
    
