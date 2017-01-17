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

"""Various functions and classes

.. module:: helpers
    :synopsis: Various functions and classes

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

import yaml

from fife.fife import DoublePoint, DoublePoint3D


class ClassProperty(property):

    """Class to make class properties"""

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()  # pylint: disable=E1101


class Enum(set):

    """A enumeration type"""

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class DoublePointYaml(DoublePoint):

    """fife.DoublePoint that can be dumped by yaml"""

    def __init__(self, x_pos_or_object=None, y_pos=None):
        if isinstance(x_pos_or_object, DoublePoint):
            x_pos = x_pos_or_object.x
            y_pos = x_pos_or_object.y
        elif type(x_pos_or_object) in (tuple, list):
            if len(x_pos_or_object) > 0:
                x_pos = x_pos_or_object[0]
            else:
                x_pos = 0
            if len(x_pos_or_object) > 1:
                y_pos = x_pos_or_object[1]
            else:
                y_pos = 0
        else:
            x_pos = x_pos_or_object
            if x_pos is None:
                x_pos = 0
            if y_pos is None:
                y_pos = 0
        DoublePoint.__init__(self, x_pos, y_pos)

    def __eq__(self, other):  # pylint: disable=arguments-differ
        if other is None:
            return False
        if not isinstance(other, DoublePoint):
            try:
                other = DoublePoint(*other[:2])
            except TypeError:
                return False
        return DoublePoint.__eq__(self, other)


def double_point_representer(dumper, data):
    """Represent a fife.DoublePoint"""
    assert isinstance(data, DoublePoint)
    pos = [data.x, data.y]
    return dumper.represent_list(pos)


def double_point_constructor(loader, node):
    """Construct a fife DoublePoint from a yaml node"""
    value = loader.construct_scalar(node)
    x_pos, y_pos = value.split(':')
    return DoublePointYaml(float(x_pos),
                           float(y_pos))


class DoublePoint3DYaml(DoublePoint3D):

    """fife.DoublePoint3D that can be dumped by yaml"""

    def __init__(self, x_pos_or_object=None, y_pos=None, z_pos=None):
        if isinstance(x_pos_or_object, DoublePoint3D):
            y_pos = x_pos_or_object.y
            z_pos = x_pos_or_object.z
            x_pos = x_pos_or_object.x
        elif type(x_pos_or_object) in (tuple, list):
            if len(x_pos_or_object) > 0:
                x_pos = x_pos_or_object[0]
            else:
                x_pos = 0
            if len(x_pos_or_object) > 1:
                y_pos = float(x_pos_or_object[1])
            else:
                y_pos = 0
            if len(x_pos_or_object) > 2:
                z_pos = float(x_pos_or_object[2])
            else:
                z_pos = 0
        else:
            x_pos = x_pos_or_object
            if x_pos is None:
                x_pos = 0
            if y_pos is None:
                y_pos = 0
            if z_pos is None:
                z_pos = 0
        DoublePoint3D.__init__(self, x_pos, y_pos, z_pos)

    def __eq__(self, other):  # pylint: disable=arguments-differ
        if other is None:
            return False
        if not isinstance(other, DoublePoint3D):
            try:
                other = DoublePoint3D(*other[:3])
            except TypeError:
                return False
        return DoublePoint3D.__eq__(self, other)


def double_point_3d_representer(dumper, data):
    """Represent a fife DoublePoint3D"""
    assert isinstance(data, DoublePoint3D)
    pos = [data.x, data.y, data.z]
    return dumper.represent_list(pos)


def double_point_3d_constructor(loader, node):
    """Construct a fife DoublePoint3d from a yaml node"""
    value = loader.construct_scalar(node)
    x_pos, y_pos, z_pos = value.split(':')
    return DoublePoint3DYaml(float(x_pos),
                             float(y_pos),
                             float(z_pos))


class FRPGDumper(yaml.SafeDumper):

    """Normal dumper with changes to save save the file in a specific style"""

    def represent_mapping(self, tag, mapping, flow_style=False):
        return yaml.SafeDumper.represent_mapping(self, tag, mapping,
                                                 flow_style)


def dump_entities(entities, stream=None):
    """Dump entities in the preferred FifeRGP style"""
    return yaml.dump_all(entities, stream, Dumper=FRPGDumper, indent=4)
