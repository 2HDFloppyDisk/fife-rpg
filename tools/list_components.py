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

"""Gather all components that are defined in a package.

.. module:: list_components
    :synopsis: Gather all components that are defined in a package.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from os.path import basename, splitext, join
from glob import glob
import sys
import argparse

import yaml

from fife_rpg.components.base import Base


def list_components(base_package, sub_package):
    """Lists the components that are in a package

    Args:
        base_package: The main package the components are in.
        Example "fife_rpg"
        sub_package: The sub package the components are in.
        Example "components"

    Returns:
        A dictionary with the components and the path to the module they are in
    """
    components = getattr(__import__(base_package, fromlist=[sub_package]),
                         sub_package)
    package_path = join(components.__path__[0])
    sys.path.append(package_path)
    component_dict = {}
    package_python_path = ".".join((base_package, sub_package))
    for python_file in glob(join(package_path, "*.py")):
        module_name = splitext(basename(python_file))[0]
        module = __import__(module_name)
        for member in dir(module):
            module_path = ".".join((package_python_path, module_name))
            component = getattr(module, member)
            try:
                if issubclass(component, Base) and component is not Base:
                    component_name = component.__name__
                    if "." in component.__module__:
                        continue
                    if component_name not in component_dict:
                        component_dict[component_name] = module_path
            except TypeError:
                pass
    return component_dict


def main():
    """Function that is run when this file is being run as a script"""
    parser = argparse.ArgumentParser(
        description='Store components in a package with their python path in '
        'a yaml file.')
    parser.add_argument("base_package",
                        help='The base package of the componets')
    parser.add_argument("sub_package", metavar="sub_package",
                        help='The python path, relative to the base_package, '
                        'where the components are')
    parser.add_argument('-o', "--output", metavar="output", type=str,
                        help='The output file')

    args = parser.parse_args()

    sub_package = args.sub_package if args.sub_package else ""

    output = args.output if args.output else "components.yaml"
    output_file = file(output, "w")
    components = {
        "Components": list_components(args.base_package, sub_package)}
    yaml.dump(components, output_file, default_flow_style=False)

if __name__ == "__main__":
    main()
