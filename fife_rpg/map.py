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

"""This module contains everything for handling fife-rpg maps

.. module:: map
    :synopsis: contains everything for handling fife-rpg maps.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from builtins import str
from builtins import object
from fife import fife
from fife.extensions.serializers import xmlanimation

from fife_rpg.components.fifeagent import FifeAgent
from fife_rpg.components.agent import Agent
from fife_rpg.components.general import General


class NoSuchRegionError(Exception):

    """Gets thrown when the code tried to access a region that does not exits
    on the map.

    Properties:
        map_name: The name of the map_name

        region_name: The name of the region_name
    """

    def __init__(self, map_name, region_name):
        Exception.__init__(self)
        self.map = map_name
        self.region = region_name

    def __str__(self):
        """Returns a string representing the exception"""
        return ("The map '%s' has no region called '%s'." %
                (self.map, self.region))


class Map(object):

    """Contains the data of a map

    Properties:
        fife_map: A fife.Map instance, representing the fife_map

        name: The internal name of the fife_map.

        view_name: The name of the map that should be displayed

        camera: The name of the default camera

        regions: A dictionary that defines specific regions on the fife_map, as
        :class:`fife.DoubleRect` instances.

        is_active: Whether the map is currently active or nor
    """

    def __init__(self, fife_map_or_filename, view_name, camera, regions,
                 application):
        self.__map = fife_map_or_filename
        self.__camera = camera
        if self.is_loaded:
            self.__setup_map_data()
        self.__view_name = view_name
        self.__regions = regions
        self.__entities = {}
        self.__application = application
        if not FifeAgent.registered_as:
            FifeAgent.register()
        if not Agent.registered_as:
            Agent.register()
        if not General.registered_as:
            General.register()

    @property
    def fife_map(self):
        """Returns the fife.Map"""
        return self.__map

    @property
    def name(self):
        """Returns the internal name of the map"""
        if self.is_loaded:
            return self.__map.getId()
        else:
            return None

    @property
    def view_name(self):
        """Returns the name of the map that is being displayed"""
        return self.__view_name

    @property
    def regions(self):
        """Returns the regions of the map"""
        return self.__regions

    @property
    def entities(self):
        """Returns the entities that are on this map"""
        return self.__entities

    @property
    def camera(self):
        """Returns the camera of the map"""
        return self.__camera

    @property
    def is_active(self):
        """Returns wheter the map is active or not"""
        return self.camera.isEnabled()

    @property
    def is_loaded(self):
        """Returns whether the map is loaded or not"""
        return isinstance(self.__map, fife.Map)

    def __getitem__(self, name):
        """Returns the entity with the given name

        Args:
            name: The name of the entity

        Raises:
            KeyError: If the map has no entity with that name

            TypeError: If the key is not a string
        """
        if not type(name) == str:
            raise TypeError("Expected key to be a string")
        for entity in self.entities:
            general = getattr(entity, General.registered_as)
            if general.identifier == name:
                return entity
        raise KeyError("The map %s has no entity with the name %s" %
                       (self.name, name))

    def get_instances_at(self, point, layer):
        """Query the main camera for instances on the specified layer.

        Args:
            point: A :class:`fife.ScreenPoint`

            layer: The :class:`fife.Layer` from which we want the instances
            or the name of the layer
        """
        if not isinstance(layer, fife.Layer):
            layer = self.get_layer(layer)
        return self.camera.getMatchingInstances(point, layer)

    def is_in_region(self, location, region):
        """Checks if a given point is inside the given region

        Args:
            location: A fife.DoublePoint instance or a tuple with 2 elements

            region: The name of the region

        Raises:
            :class:`fife_rpg.map.NoSuchRegionError` if the specified region
            does not exist.
        """
        if isinstance(location, tuple) or isinstance(location, list):
            location = fife.DoublePoint(location[0], location[1])
        if region not in self.regions:
            raise NoSuchRegionError(self.name, region)
        else:
            return self.regions[region].contains(location)

    def __setup_map_data(self):
        """Sets up the map data after the map was loaded"""
        self.__camera = self.__map.getCamera(self.__camera)
        cameras = self.__map.getCameras()
        for camera in cameras:
            camera.setEnabled(False)

    def activate(self):
        """Activates the map"""
        self.__application.world.add_entity_delete_callback(
            self.cb_entity_delete)
        if not self.is_loaded:
            engine = self.__application.engine
            loader = fife.MapLoader(engine.getModel(),
                                    engine.getVFS(),
                                    engine.getImageManager(),
                                    engine.getRenderBackend())

            if loader.isLoadable(self.__map):
                self.__map = loader.load(self.__map)
                self.__setup_map_data()
            else:
                raise RuntimeError("Can't load mapfile %s" % str(self.__map))
            self.update_entities()
            self.__application.map_loded(self.__map.getId())
        else:
            self.__application.update_agents(self.__map.getId())
        self.camera.setEnabled(True)

    def deactivate(self):
        """Deactivates the map"""
        self.camera.setEnabled(False)

    def update_entities(self):
        """Update the maps entites from the entities of the world
        """
        extent = self.__application.world[...]
        self.__entities = getattr(extent,
                                  Agent.registered_as).map == self.name

    def update_entities_fife(self):
        """Updates the fife instances to the values of the agent"""
        old_entities = self.entities.copy()
        for entity in old_entities:
            fifeagent = getattr(entity, FifeAgent.registered_as)
            if fifeagent:
                agent = getattr(entity, Agent.registered_as)
                if agent.new_map is not None and agent.new_map != self.name:
                    self.remove_entity(str(entity.identifier))
                    continue
                location = fifeagent.instance.getLocation()
                if agent.new_layer is not None:
                    location.setLayer(self.get_layer(agent.layer))
                if agent.new_position is not None:
                    location.setExactLayerCoordinates(
                        fife.ExactModelCoordinate(
                            *agent.new_position))
                fifeagent.instance.setLocation(location)
                if agent.new_rotation is not None:
                    fifeagent.instance.setRotation(agent.rotation)
                agent.new_map = None
                agent.new_layer = None
                agent.new_position = None
                agent.new_rotation = None

    def update_entitities_agent(self):
        """Update the values of the agent component of the maps entities"""
        for entity in self.entities:
            fifeagent = getattr(entity, FifeAgent.registered_as)
            if fifeagent:
                agent = getattr(entity, Agent.registered_as)
                location = fifeagent.behaviour.location
                agent.position = (location.x, location.y, location.z)
                agent.rotation = fifeagent.behaviour.rotation

    def remove_entity(self, identifier):
        """Removes an entity from the map

        Args:
            identifier: The name of the entity

        Raises:
            KeyError: If the map has no entity with that name

            TypeError: If the identifier is not a string
        """
        try:
            entity = self[identifier]
            fifeagent = getattr(entity, FifeAgent.registered_as)
            instance = fifeagent.layer.getInstance(identifier)
            fifeagent.layer.deleteInstance(instance)
            instance = fifeagent.layer.getInstance(identifier)
            fifeagent.layer = None
            fifeagent.behaviour = None
            agent = getattr(entity, Agent.registered_as)
            agent.map = ""
            self.update_entities()
        except KeyError as error:
            raise error
        except TypeError as error:
            raise TypeError("Expected identifier to be a string")

    def get_layer(self, layer):
        """Returns the layer with the given name

        Args:
            layer: The name of the layer
        """
        return self.fife_map.getLayer(layer)

    def get_light_renderer(self):
        """Returns the light renderer of the current camera"""
        return fife.LightRenderer.getInstance(self.camera)

    def __create_render_node(self, agent=None, layer=None, location=None,
                             point=None):
        """Creatss a fife.RendererNode.

        Arguments:
            agent: The name of the agent the light should be attached too. If
            empty or None this will be ignored. Please note that the layer and
            location have to be set if this is empty or None.

            layer: The name of the layer the light originates from. Lights will
            illuminate lower layers, but not higher ones. If empty or None this
            will be ignored.

            location: The relative or absolute location of the light depending
            on whether the agent was set or not. A list with two or three
            values.
            If None this will be ignored.

            point: The relative or absolute window position of the light as
            a list with 2 values or a fife.Point.
            This differs from location as it is in pixels and (0, 0) is the
            upper left position of the window.
        """
        if agent is not None and agent != "":
            entity = self.__application.world.get_entity(agent)
            if entity in self.entities:
                fifeagent = getattr(entity, FifeAgent.registered_as)
                agent = fifeagent.instance
            else:
                raise TypeError("The map %s has no entity %s" % (self.name,
                                                                 agent))
        else:
            agent = None
        if layer is not None and layer != "":
            map_layer = self.get_layer(layer)
            if map_layer is None:
                raise TypeError("No such layer: %s" % (layer))
            layer = map_layer
        elif agent is not None:
            layer = fifeagent.layer
        else:
            layer = None
        if location:
            if layer is not None:
                coords = fife.DoublePoint3D(*location)
                location = fife.Location()
                location.setLayer(layer)
                location.setMapCoordinates(coords)
            else:
                raise TypeError(
                    "The location was set, but not agent or layer.")
        else:
            location = None
        if point is not None and not isinstance(point, fife.Point):
            point = fife.Point(*point)
        arguments = []
        if agent is not None:
            arguments.append(agent)
        if location is not None:
            arguments.append(location)
        if layer is not None:
            arguments.append(layer)
            self.get_light_renderer().addActiveLayer(layer)
        if point is not None:
            arguments.append(point)
        if not arguments:
            raise TypeError("A light needs either an agent"
                            ", a location and a layer"
                            ", or a point")
        node = fife.RendererNode(*arguments)
        return node

    def add_simple_light(self, group, intensity, radius, subdivisions, color,
                         stretch=None, agent=None, layer=None, location=None,
                         point=None, blend_mode=(-1, -1)):
        """Adds a simple light to the map.

        Arguments:

            group: The name of the group the light should be put in.

            intensity: The intensity of the radius as a value between 0 and 255

            radius: The radius of the light as a float

            subdivisions: The number of subdivisions of the light. More
            subdivisions mean smoother light.

            color: The color of the light either as a list with with three
            values between 0 and 255 or a fife.Color

            stretch: The x and y stretch factor of the light as a list
            with two float values. If None it will default to both 1.0.

            agent: The name of the agent the light should be attached too. If
            empty or None this will be ignored. Please note that the layer and
            location have to be set if this is empty or None.

            layer: The name of the layer the light originates from. Lights will
            illuminate lower layers, but not higher ones. If empty or None this
            will be ignored.

            location: The relative or absolute location of the agent depending
            on whether the agent was set or not. A list with two or three
            values.
            If None this will be ignored.

            point: The relative or absolute window position of the light as
            a list with 2 values or a fife.Point.
            This differs from location as it is in pixels and (0, 0) is the
            upper left position of the window.

            blend_mode: A list with 2 values for the source and
            destination blend modes. If not passed the default values of FIFE
            will be used.

        Returns:
            The light info of the added light
        """
        node = self.__create_render_node(agent, layer, location, point)
        if stretch is None:
            stretch = (1.0, 1.0)
        if isinstance(color, fife.Color):
            color = (color.getR(), color.getG(), color.getB())
        arguments = (group, node, intensity, radius, subdivisions)
        arguments += tuple(stretch)
        arguments += tuple(color)
        arguments += tuple(blend_mode)
        light_renderer = self.get_light_renderer()
        light_renderer.addSimpleLight(*arguments)
        return light_renderer.getLightInfo(group)[-1]

    def add_light_from_lightmap(self, group, lightmap, size=None, agent=None,
                                layer=None, location=None, point=None,
                                blend_mode=(-1, -1)):
        """Adds a light that uses a lightmap.

        Arguments:

            group: The name of the group the light should be put in.

            lightmap: The path to the lightmap image file or a fife.Image

            size: A list with 2 values that set to what size the lightmap
            should be resized. If None this will be ignored.

            agent: The name of the agent the light should be attached too. If
            empty or None this will be ignored. Please note that the layer and
            location have to be set if this is empty or None.

            layer: The name of the layer the light originates from. Lights will
            illuminate lower layers, but not higher ones. If empty or None this
            will be ignored.

            location: The relative or absolute location of the agent depending
            on whether the agent was set or not. A list with two or three
            values.
            If None this will be ignored.

            point: The relative or absolute window position of the light as
            a list with 2 values or a fife.Point.
            This differs from location as it is in pixels and (0, 0) is the
            upper left position of the window.

            blend_mode: A list with 2 values for the source and
            destination blend modes. If not passed the default values of FIFE
            will be used.

        Returns:
            The light info of the added light
        """
        node = self.__create_render_node(agent, layer, location, point)
        if not isinstance(lightmap, fife.Image):
            engine = self.__application.engine
            lightmap = engine.getImageManager().load(lightmap)
        light_renderer = self.get_light_renderer()
        if size is not None:
            light_renderer.resizeImage(group, node, lightmap,
                                       *(size + blend_mode))
        else:
            light_renderer.addImage(group, node, lightmap, *blend_mode)
        return light_renderer.getLightInfo(group)[-1]

    def add_light_from_animation(self, group, animation, agent=None,
                                 layer=None, location=None, point=None,
                                 blend_mode=(-1, -1)):
        """Adds a light that uses an animation lightmap.

        Arguments:

            group: The name of the group the light should be put in.

            animation: The path to a xml file that contains the animation data
            or a fife.Animation.

            agent: The name of the agent the light should be attached too. If
            empty or None this will be ignored. Please note that the layer and
            location have to be set if this is empty or None.

            layer: The name of the layer the light originates from. Lights will
            illuminate lower layers, but not higher ones. If empty or None this
            will be ignored.

            location: The relative or absolute location of the agent depending
            on whether the agent was set or not. A list with two or three
            values.
            If None this will be ignored.

            point: The relative or absolute window position of the light as
            a list with 2 values or a fife.Point.
            This differs from location as it is in pixels and (0, 0) is the
            upper left position of the window.

            blend_mode: A list with 2 values for the source and
            destination blend modes. If not passed the default values of FIFE
            will be used.

        Returns:
            The light info of the added light
        """
        node = self.__create_render_node(agent, layer, location, point)
        if not isinstance(animation, fife.Animation):
            animation = xmlanimation.loadXMLAnimation(
                self.__application.engine,
                animation)
        light_renderer = self.get_light_renderer()
        light_renderer.addAnimation(group, node, animation, *blend_mode)
        return light_renderer.getLightInfo(group)[-1]

    def enable_camera(self, name):
        """Enables the camera with the given name

        Args:

            name: The name of the camera
        """
        try:
            self.fife_map.getCamera(name).setEnabled(True)
        except:  # pylint: disable=bare-except
            pass

    def disable_camera(self, name):
        """Enables the camera with the given name

        Args:

            name: The name of the camera
        """
        try:
            self.fife_map.getCamera(name).setEnabled(False)
        except:  # pylint: disable=bare-except
            pass

    def move_camera_to(self, position):
        """Move the current camera to the given position

        Args:

            position: Position on the map to move the camera to
        """
        location = self.camera.getLocation()
        coords = fife.ExactModelCoordinate(*position)
        location.setMapCoordinates(coords)
        self.camera.setLocation(location)

    def move_camera_by(self, vector):
        """Move the current camera by the amount given by the vector

        Args:

            vector: A list of 2 numbers that determine the movement vector
        """
        location = self.camera.getLocation()
        coords = location.getMapCoordinates()
        position_offset = fife.DoublePoint3D(*vector)
        coords += position_offset
        location.setMapCoordinates(coords)
        self.camera.setLocation(location)

    def cb_entity_delete(self, entity):
        """Called when an entiy is about to be deleted"""
        if entity in self.entities:
            self.remove_entity(entity.identifier)
