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

from fife_rpg.systems import GameEnvironment
from fife_rpg import ControllerBase

class DialogueSection(object):
    """Represents a section of a dialogue

    Properties:
        talker: The Entity that is talking

        text: The text that is being said

        condition: String that is being evaluated

        commands: Commands that are to be executed when 
        the section is displayed

        responses: Possible responses for this section
        """
    
    def __init__(self, talker, text, 
                 condition=None, commands=None, responses=None):
        self.talker = talker
        self.text = text
        self.condition = condition or "True"
        self.commands = commands or []
        self.responses = responses or []

class Dialogue(object):
    """Represents a single dialogue

    Properties:
        world: RPGWorld that the dialogue is run on

        sections: The sections of the dialogue
        
        current_section: The section that is currently active
    """

    def __init__(self, world, dialogue_data):
        """Create the sections based on the dialogue data
        
        Args:
            dialogue_data: A dictionary containing the dialogue data
        """
        self.world = world
        self.current_section = None
        self.sections = {}
        sections_data = dialogue_data["Sections"]
        self.create_sections(sections_data)
        greetings_data = dialogue_data["Greetings"]
        self.select_greeting(greetings_data)
        
    def get_game_environment(self, section):
        """Checks if the GameEnvironment system is registered and returns 
        its current values and additional values used by the dialogues.
        
        Args:
            section: A :class:`fife_rpg.dialogue.DialogueSection`. This will be 
            used to get the additional values
        """
        game_environment = GameEnvironment.registered_as
        if game_environment:
            game_environment = getattr(self.world.systems, 
                                       game_environment)
            env_globals, env_locals = game_environment.get_environement()
        else:
            env_globals, env_locals = {}
            env_globals["__builtins__"] = None
            print ("The dialogue controller needs the GameEnvironment system "
                   "to function properly.")
        env_globals["dialogue_talker"] = self.world.get_entity(section.talker)
        return env_globals, env_locals
    
    @property
    def possible_responses(self):
        """Returns a dictionary of the possible responses of the current section"""
        if not self.current_section or not self.current_section.responses:
            return []
        possible_responses = {}
        for response_name in self.current_section.responses:
            response = self.sections[response_name]
            env_globals, env_locals = self.get_game_environment(response)
            if eval(response.condition, env_globals, env_locals):
                possible_responses[response_name] = response
        return possible_responses
    
    @property
    def is_dialogue_finished(self):
        """Returns whether the dialogue is finished or not"""
        return bool(self.possible_responses)
    
    def run_section(self, section):
        """Runs the commands of the section
        
        Args:
            section: A :class:`fife_rpg.dialogue.DialogueSection`
        """
        env_globals, env_locals = self.get_game_environment(section)
        for command in section.commands:
            exec(command, env_globals, env_locals) #pylint:disable=W0122
            
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
        if section_data.has_key("condition"):
            condition = section_data["condition"]
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
        env_globals, env_locals = self.get_game_environment(section)
        text_vals = env_globals.copy()
        text_vals.update(env_locals)
        section.text = _(section.text).format(**text_vals) #pylint: disable=E0602        
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
        """Selects the first greeting which condition passes
        
        Args:
            greetings_data: A dictionary containing the data of the greetings
        """
        for greeting_data in greetings_data.itervalues():
            greeting = self.create_section(greeting_data)
            env_globals, env_locals = self.get_game_environment(greeting)
            if eval(greeting.condition, env_globals, env_locals):
                self.current_section = greeting
                self.run_section(greeting)

class DialogueController(ControllerBase):
    """Controller that handles Dialogues

    Properties:
        application: The application that created this controller

        view: The view that is used by this controller
    """
    
    def __init__(self, view, application):
        ControllerBase.__init__(self, view, application)
        self.dialogues = {}
        self.current_dialogue = None
        
    def add_dialogue(self, identifier, dialogue_data):
        """Add a dialogue to the controller
        
        Args:
            identifier: The name of the dialogue
            
            dialogue_data: The data of the dialogue
        """
        self.dialogues[identifier] = dialogue_data
    
    def add_dialogue_from_file(self, filename):
        """Loads a dialogue from a file and adds it to the controller
        
        Args:
            filename: The path to the file
        """
        dialogue_file = file(filename, "r")
        dialogue_data = yaml.load(dialogue_file)
        self.add_dialogue(dialogue_data["Identifier"], dialogue_data)
        
    def start_dialogue(self, identifier):
        """Starts a dialogue
        
        Args:
            identifier: The name of the dialogue to start
        """
        if not self.dialogues.has_key(identifier):
            raise KeyError("Dialogue '%s' not found" % identifier)
        dialogue_data = self.dialogues[identifier]
        self.current_dialogue = Dialogue(self.application.world, dialogue_data)
        
    def end_dialogue(self):
        """Ends the current dialogue"""
        self.current_dialogue = None
