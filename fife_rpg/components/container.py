#!/usr/bin/python
# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
from operator import attrgetter

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The Container component and functions

.. module:: container
    :synopsis: The Container component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base
from fife_rpg.components.containable import Containable


class Container(Base):

    """Component that allows an entity to contain one or more child entities.

    Fields:
        max_bulk: How much place the container has

        max_slots: How many slots the container has
    """

    dependencies = [Containable]

    def __init__(self):
        Base.__init__(self, max_bulk=float, max_slots=int)

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""

        fields = self.fields.keys()
        return fields

    @classmethod
    def register(cls, name='Container', auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """

        return super(Container, cls).register(name, auto_register)


class BulkLimitError(Exception):

    """Error that gets raised when the item would exceed the
    bulk limit of the container.

    Properties:
        bulk: What the bulk would be

        max_bulk: What the max bulk is
    """

    def __init__(self, bulk, max_bulk):
        Exception.__init__(self)
        self.bulk = bulk
        self.max_bulk = max_bulk

    def __str__(self):
        """Returns the string representing the exception"""

        return 'Item would exceed the bulk limit of the container.'


class NoFreeSlotError(Exception):

    """Error that gets raised when the container has no free slots."""

    def __str__(self):
        """Returns the string representing the exception"""

        return "Container can't hold any more items."


def get_items(container, item_type=None):
    """Return a list of all items of a given type in a container.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component

        item_type: Type of items. If none all items are returned.
    """
    world = container.world
    containables = getattr(world[...], Containable.registered_as)
    in_container = containables.container == container.identifier
    if item_type is None:
        return list(in_container)
    else:
        with_type = containables.item_type == item_type
        return list(in_container & with_type)


def get_free_slot(container):
    """Returns the first slot of the container that is not occupied.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component

    Returns:
        The index of a free slot if there is any.

    Raises:
        :class:`fife_rpg.components.container.NoFreeSlotError`
        if there is no free slot.
    """

    in_container = get_items(container)
    container_component = getattr(container, Container.registered_as)
    used_slots = set()
    for child in in_container:
        child_component = getattr(child, Containable.registered_as)
        used_slots.add(child_component.slot)
    if container_component.max_slots > 0:
        usable_slots = set(range(container_component.max_slots))
    else:
        try:
            usable_slots = set(range(max(used_slots) + 2))
        except ValueError:
            usable_slots = set((0,))
    try:
        return min(usable_slots - used_slots)
    except ValueError:
        raise NoFreeSlotError


def get_total_bulk(container):
    """Returns the bulk of all items in the container.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component
    """

    total_bulk = 0
    for child in get_items(container):
        child_component = getattr(child,
                                  Containable.registered_as)
        total_bulk += child_component.bulk * child_component.current_stack
    return total_bulk


def get_total_weight(container):
    """Returns the weight of all items in the container.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component
    """

    total_weight = 0
    for child in get_items(container):
        child_component = getattr(child,
                                  Containable.registered_as)
        total_weight += child_component.weight
    return total_weight


def get_item(container, slot_or_type):
    """Returns the item that is in the slot, or has the given type.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component

        slot_or_type: The index of the slot, or an item type
    """

    if type(slot_or_type) == int:
        for child in get_items(container):
            child_component = getattr(child, Containable.registered_as)
            if child_component.slot == slot_or_type:
                return child
    else:
        for child in get_items(container):
            child_component = getattr(child, Containable.registered_as)
            if child_component.item_type == slot_or_type:
                return child
    return None


def remove_item(container, slot_or_type):
    """Removes the item at the given slot, or with the given type.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component

        slot_or_type: The index of the slot, or an item type
    """

    container_data = getattr(container, Container.registered_as)
    if type(slot_or_type) == int:
        item = get_item(container, slot_or_type)
        if item:
            item = getattr(item, Containable.registered_as)
            item.container = None
            item.slot = -1
            if container_data.max_slots <= 0:
                entities = get_items(container)
                items = []
                for entity in entities:
                    items.append(getattr(entity, Containable.registered_as))
                items = sorted(items, key=attrgetter("slot"))
                for x in xrange(len(items)):
                    item = items[x]
                    item.slot = x


def take_item(container, slot_or_type):
    """Moves the item at the given slot, or with the given type,
    out of the container and returns it.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component

        slot_or_type: The index of the slot, or an item type

    Returns:
        The item as an RPGEntity
    """

    item = get_item(container, slot_or_type)
    if item:
        item_data = getattr(item, Containable.registered_as)
        remove_item(container, item_data.slot)
    return item


def merge_stack(source, dest):
    """Merge the dest stack into the source stack

    Args:
        source: The stack that will be used to fill the dest stack

        dest: The stack that will be filled by the source stack
    """
    source_data = getattr(source, Containable.registered_as)
    dest_data = getattr(dest, Containable.registered_as)
    free = dest_data.max_stack - dest_data.current_stack
    if free > source_data.current_stack:
        to_add = source_data.current_stack
    else:
        to_add = free
    if dest_data.container is not None:
        container = source.world.get_entity(dest_data.container)
        total_bulk = get_total_bulk(container)
        container_data = getattr(container, Container.registered_as)
        total_bulk += source_data.bulk * to_add
        if total_bulk > container_data.max_bulk:
            max_bulk = container_data.max_bulk
            exceed_bulk = total_bulk - max_bulk
            exceed_item = (exceed_bulk / source_data.bulk +
                           (exceed_bulk % source_data.bulk))
            to_add = to_add - exceed_item
    dest_data.current_stack += to_add
    source_data.current_stack -= to_add


def put_item(container, item, slot=-1):
    """Puts the item at the given slot in the container and returns an
    item previously at the slot or the free stack.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        container component

        item: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a
        containable component

        slot: The slot where to put the item. Defaults to first free slot.

    Raises:
        :class:`fife_rpg.components.container.BulkLimitError` if the item would
        exceed the containers bulk.
    """

    container_data = getattr(container, Container.registered_as)
    item_data = getattr(item, Containable.registered_as)
    if slot == -1:
        if item_data.current_stack < item_data.max_stack:
            stacks = get_items(container, item_data.item_type)
            for stack in stacks:
                if stack.identifier == item.identifier:
                    continue
                merge_stack(item, stack)
                if item_data.current_stack == 0:
                    return item
                total_bulk = get_total_bulk(container)
                if total_bulk + item_data.bulk > container_data.max_bulk:
                    total_bulk += item_data.bulk * item_data.current_stack
                    raise BulkLimitError(total_bulk, container_data.max_bulk)

        slot = get_free_slot(container)
    old_item = get_item(container, slot)
    total_bulk = get_total_bulk(container)
    if old_item:
        old_item_data = getattr(old_item, Containable.registered_as)
        if (old_item_data.item_type == item_data.item_type and
                old_item_data.current_stack < old_item_data.max_stack):
            merge_stack(item, old_item)
            total_bulk = get_total_bulk(container)
            if total_bulk + item_data.bulk > container_data.max_bulk:
                total_bulk += item_data.bulk * item_data.current_stack
                raise BulkLimitError(total_bulk, container_data.max_bulk)
            elif item_data.current_stack == 0:
                return item
            else:
                return item_data
        else:
            total_bulk -= old_item_data.bulk
    elif container_data.max_slots <= 0:
        slot = get_free_slot(container)
    total_bulk += item_data.bulk * item_data.current_stack
    if total_bulk > container_data.max_bulk:
        raise BulkLimitError(total_bulk, container_data.max_bulk)
    remove_item(container, slot)
    if item_data.container:
        remove_item(item_data.container, item_data.slot)
    item_data.container = container.identifier
    item_data.slot = slot
    return old_item
