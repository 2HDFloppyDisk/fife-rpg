#! /usr/bin/env python2

# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module parses a dialogue file and outputs the texts to a gettext
template file.

.. module:: pygettext_dialogue
    :synopsis: Writes dialogue strings to a template file.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
import argparse
import os

import yaml


def main():
    """Function that is run when this file is being run as a script"""
    parser = argparse.ArgumentParser(
        description='Get message strings from fife-rpg dialogue files.')
    parser.add_argument("input",
                        help='The input file')
    parser.add_argument('-o', "--output", metavar="output", type=str,
                        help='The output file')

    args = parser.parse_args()

    try:
        dialogue_file = file(args.input, "r")
    except IOError as error:
        print "Cannot open input file '%s'" % args.input
        print error
        dialogue_file = None

    if dialogue_file:
        if args.output:
            messages_filename = args.output
        else:
            messages_filename = "messages.pot"
        messages_file = file(messages_filename, "w")
        input_filename = os.path.basename(args.input)
        print "Writing dialogue strings from %s to %s" % (input_filename,
                                                          messages_filename)
        dialogue_data = yaml.load(dialogue_file)
        dialogue_file.close()
        sections_data = dialogue_data["Sections"]
        sections_data.update(dialogue_data["Greetings"])
        for name, section in sections_data.iteritems():
            lines = []
            lines.append("\n#%s - %s\n" % (input_filename, name))
            lines.append("msgid \"%s\"\n" % section["text"])
            lines.append("msgstr \"\"\n")
            messages_file.writelines(lines)
        print "Success"


if __name__ == '__main__':
    main()
