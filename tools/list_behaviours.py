#! /usr/bin/env python
from os.path import basename, splitext, join
from glob import glob
import sys
import argparse

import yaml

from fife_rpg.behaviours.base import Base


def list_components(base_package, sub_package):
    """Lists the behaviours that are in a package

    Args:
        base_package: The main package the behaviours are in.
        Example "fife_rpg"
        sub_package: The sub package the behaviours are in.
        Example "behaviours"

    Returns:
        A dictionary with the behaviours and the path to the module they are in
    """
    behaviours = getattr(__import__(base_package, fromlist=[sub_package]),
                     sub_package)
    package_path = join(behaviours.__path__[0])
    sys.path.append(package_path)
    behaviour_dict = {}
    package_python_path = ".".join((base_package, sub_package))
    for python_file in glob(join(package_path, "*.py")):
        module_name = splitext(basename(python_file))[0]
        module = __import__(module_name)
        for member in dir(module):
            module_path = ".".join((package_python_path, module_name))
            behaviour = getattr(module, member)
            try:
                if (issubclass(behaviour, Base)):
                    behaviour_name = behaviour.__name__
                    if "." in behaviour.__module__:
                        continue
                    if not behaviour_name in behaviour_dict:
                        behaviour_dict[behaviour_name] = module_path
            except TypeError:
                pass
    return behaviour_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Store behaviours in a package with their python path'
            'in a yaml file.')
    parser.add_argument("base_package",
                       help='The base package of the componets')
    parser.add_argument("sub_package", metavar="sub_package",
                       help='The python path, relative to the base_package, '
                       'where the behaviours are')
    parser.add_argument('-o', "--output", metavar="output", type=str,
                       help='The output file')

    args = parser.parse_args()

    sub_package = args.sub_package if args.sub_package else ""

    output = args.output if args.output else "behaviours.yaml"
    output_file = file(output, "w")
    behaviours = {"Behaviours": list_components(args.base_package,
                                                sub_package)}
    yaml.dump(behaviours, output_file, default_flow_style=False)
