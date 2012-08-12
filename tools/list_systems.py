#! /usr/bin/env python
from os.path import basename, splitext, join
from glob import glob
import sys
import argparse

import yaml

from fife_rpg.systems.base import Base

def list_systems(base_package, sub_package):
    """Lists the systems that are in a package

    Args:
        base_package: The main package the systems are in. Example "fife_rpg"
        sub_package: The sub package the systems are in. Example "systems"

    Returns:
        A dictionary with the systems and the path to the module they are in
    """
    systems = getattr(__import__(base_package, fromlist=[sub_package]),
                     sub_package)
    package_path = join(systems.__path__[0])
    sys.path.append(package_path)
    system_dict = {}
    for python_file in glob(join(package_path, "*.py")):
        module_name = splitext(basename(python_file))[0]
        module = __import__(module_name)
        for member in dir(module):
            module_path = ".".join((base_package,
                                    sub_package,
                                    module_name))
            system = getattr(module, member)
            try:
                if (issubclass(system, Base) and not system is Base):
                    system_name = system.__name__
                    if not system_name in system_dict:
                        system_dict[system_name] = module_path
            except TypeError:
                pass
    return system_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Store systems in a package with their python path in a '
            'yaml file.')
    parser.add_argument("base_package",
                       help='The base package of the componets')
    parser.add_argument("sub_package", metavar="sub_package",
                       help='The python path, relative to the base_package, '
                       'where the systems are')
    parser.add_argument('-o', "--output", metavar="output", type=str,
                       help='The output file')
    
    args = parser.parse_args()
    
    sub_package = args.sub_package if args.sub_package else ""
    
    output = args.output if args.output else "systems.yaml"
    output_file = file(output, "w")
    systems = list_systems(args.base_package, sub_package)
    yaml.dump(systems, output_file, default_flow_style=False)
