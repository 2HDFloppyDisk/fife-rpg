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
#

"""This module contains the the functions and classes for playing dialogues.

.. module:: controllers
    :synopsis: Functions and classes for playing dialogues.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
import yaml

from fife_rpg.systems import GameVariables
from fife_rpg import ControllerBase
from fife_rpg.systems.scriptingsystem import ScriptingSystem
from fife_rpg.exceptions import NotRegisteredError

class DialogueSection(object):
    """Represents a section of a dialogue

    Properties:
        talker: The Entity that is talking

        text: The text that is being said

        conditions: List of conditions that are evaluated

        commands: Commands that are to be executed when 
        the section is displayed

        responses: Possible responses for this section
        """
    
    def __init__(self, talker, text, 
                 conditions=None, commands=None, responses=None):
        self.talker = talker
        self.text = text
        self.conditions = conditions
        self.commands = commands or []
        self.responses = responses or []

class Dialogue(object):
    """Represents a single dialogue

    Properties:
        world: |RPGWorld| that the dialogue is run on

        sections: A list of |DialogueSection|
        
        current_section: The |DialogueSection| that is currently active
    """

    def __init__(self, world, dialogue_data):
        """Create the sections based on the dialogue data
        
        Args:
            dialogue_data: A dictionary containing the dialogue data
        """
        game_variables = GameVariables.registered_as
        if not game_variables:
            raise NotRegisteredError("GameVariables")
        scripting = ScriptingSystem.registered_as
        if not scripting:
            raise NotRegisteredError("ScriptingSystem")
        self.world = world
        self.current_section = None
        self.sections = {}
        sections_data = dialogue_data["Sections"]
        self.create_sections(sections_data)
        greetings_data = dialogue_data["Greetings"]
        self.select_greeting(greetings_data)
        
    def get_dialogue_variables(self, section):
        """Returns the game variables combined with dialogue specific
        variables.
        
        Args:
            section: A |DialogueSection|. This will be
            used to get dialogue variables
        """
        game_variables = getattr(self.world.systems, 
                                   "game_variables")
        variables = game_variables.get_variables()
        variables["DialogueTalker"] = self.world.get_entity(section.talker)
        return variables
    
    @property
    def possible_responses(self):
        """Returns a dictionary of the possible responses of the current section"""
        if not self.current_section or not self.current_section.responses:
            return []
        possible_responses = {}
        for response_name in self.current_section.responses:
            response = self.sections[response_name]
            if (response.conditions is None or
                ScriptingSystem.check_condition(self.world.application,
                                                response.conditions)): 
                possible_responses[response_name] = response
        return possible_responses
    
    @property
    def is_dialogue_finished(self):
        """Returns whether the dialogue is finished or not"""
        return not bool(self.possible_responses)
    
    def run_section(self, section):
        """Runs the commands of the section
        
        Args:
            section: A |DialogueSection|
        """
        variables = self.get_dialogue_variables(section)
        for command in section.commands:
            name = command["Name"]
            args = []
            for arg in command["Args"]:
                value = arg.format(**variables)
                args.append(value)
            arg_string = " ".join(args)
            command_string = "%s %s" % (name, arg_string)
            self.world.application.execute_console_command(command_string)
            
    def select_response(self, response_name):
        """Selects the given response and performs its actions
        
        Args:
            response_name: The name of the response
        """
        if (not self.sections.has_key(response_name) or
            not response_name in self.possible_responses):
            raise KeyError("There is no '%s' response available" % response_name)
        response = self.sections[response_name]
        self.current_section = response
        self.run_section(response)


    def create_section(self, section_data):
        """Create a section and return it
        
        Args: 
            section_data: A dictionary containing the data of a section
        """
        talker = section_data["talker"]
        text = section_data["text"]
        if section_data.has_key("conditions"):
            condition = section_data["conditions"]
        else:
            condition = None
        if section_data.has_key("commands"):
            commands = section_data["commands"]
        else:
            commands = None
        if section_data.has_key("responses"):
            responses = section_data["responses"]
        else:
            responses = None
        section = DialogueSection(talker, text, condition, commands, responses)
        variables = self.get_dialogue_variables(section)
        #pylint: disable=E0602
        section.text = _(section.text).format(**variables)
        #pylint: enable=E0602       
        return section

    def create_sections(self, sections_data):
        """Create the dialogue sections
        
        Args:
            sections_data: A dictionary containing the data of the sections
        """
        for section_name, section_data in sections_data.iteritems():
            section = self.create_section(section_data)
            self.sections[section_name] = section 

    def select_greeting(self, greetings_data):
        """Selects the first greeting which conditions passes
        
        Args:
            greetings_data: A dictionary containing the data of the greetings
        """
        for greeting_data in greetings_data:
            greeting = self.create_section(greeting_data)
            if (greeting.conditions is None or
                ScriptingSystem.check_condition(self.world.application,
                                                greeting.conditions)): 
                self.current_section = greeting
                self.run_section(greeting)
                break

class DialogueController(ControllerBase):
    """Controller that handles Dialogues

    Properties:
        application: The |Application| that created this controller

        view: The |View| that is used by this controller
        
        dialogue: The active |Dialogue|
    """
    
    def __init__(self, view, application, dialogue):
        """Args:
        
            dialogue: A dictionary with the dialogue data, or a string
            with the name of a file to load, or a |Dialogue| instance.
        """
        ControllerBase.__init__(self, view, application)
        if(isinstance(dialogue, str)):
            dialogue_file = self.application.engine.getVFS().open(dialogue)
            dialogue = yaml.load(dialogue_file)
        if(isinstance(dialogue, dict)):
            self.dialogue = Dialogue(self.application.world, dialogue)
        else:
            self.dialogue = dialogue        

    @property
    def possible_responses(self):
        """Returns a dictionary of the possible responses of the active
        dialogue"""
        return self.dialogue.possible_responses

    @property
    def is_dialogue_finished(self):
        """Returns whether the active dialogue is finished or not"""
        return self.dialogue.is_dialogue_finished
    
    @property
    def current_section(self):
        """Returns the current section of the active dialogue"""
        return self.dialogue.current_section

    def select_response(self, response_name):
        """Selects the given response and performs its actions
        
        Args:
            response_name: The name of the response
        """
        return self.dialogue.select_response(response_name)        

    def pump(self, time_delta):
        """Performs actions every frame

        Args:
            time_delta: Time that passed since the last call
        """
        ControllerBase.pump(self, time_delta)
        if self.is_dialogue_finished:
            self.manager.remove_mode(self)