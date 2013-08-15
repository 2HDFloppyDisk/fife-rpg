#! /usr/bin/env python
from os.path import basename, splitext, join
from glob import glob
import sys
import argparse

import yaml

from fife_rpg.components.base import Base

def list_components(base_package, sub_package):
    """Lists the components that are in a package

    Args:
        base_package: The main package the components are in. Example "fife_rpg"
        sub_package: The sub package the components are in. Example "components"

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
                if (issubclass(component, Base) and not component is Base):
                    component_name = component.__name__
                    if "." in component.__module__:
                        continue
                    if not component_name in component_dict:
                        component_dict[component_name] = module_path
            except TypeError:
                pass
    return component_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Store components in a package with their python path in a '
            'yaml file.')
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
    components = {"Components": list_components(args.base_package, sub_package)}
    yaml.dump(components, output_file, default_flow_style=False)
