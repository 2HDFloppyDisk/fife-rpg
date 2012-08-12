#! /usr/bin/env python
from os.path import basename, splitext, join
from glob import glob
import sys
import argparse

import yaml

from fife_rpg.actions.base import Base

def list_actions(base_package, sub_package):
    """Lists the actions that are in a package

    Args:
        base_package: The main package the actions are in. Example "fife_rpg"
        sub_package: The sub package the actions are in. Example "actions"

    Returns:
        A dictionary with the actions and the path to the module they are in
    """
    actions = getattr(__import__(base_package, fromlist=[sub_package]),
                     sub_package)
    package_path = join(actions.__path__[0])
    sys.path.append(package_path)
    action_dict = {}
    for python_file in glob(join(package_path, "*.py")):
        module_name = splitext(basename(python_file))[0]
        module = __import__(module_name)
        for member in dir(module):
            module_path = ".".join((base_package,
                                    sub_package,
                                    module_name))
            action = getattr(module, member)
            try:
                if (issubclass(action, Base) and not action is Base):
                    if "." in action.__module__:
                        continue
                    action_name = action.__name__
                    if not action_name in action_dict:
                        action_dict[action_name] = module_path
            except TypeError:
                pass
    return action_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Store actions in a package with their python path in a '
            'yaml file.')
    parser.add_argument("base_package",
                       help='The base package of the componets')
    parser.add_argument("sub_package", metavar="sub_package",
                       help='The python path, relative to the base_package, '
                       'where the actions are')
    parser.add_argument('-o', "--output", metavar="output", type=str,
                       help='The output file')
    
    args = parser.parse_args()
    
    sub_package = args.sub_package if args.sub_package else ""
    
    output = args.output if args.output else "actions.yaml"
    output_file = file(output, "w")
    actions = {"Actions": list_actions(args.base_package, sub_package)}
    yaml.dump(actions, output_file, default_flow_style=False)
