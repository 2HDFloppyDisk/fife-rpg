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
        children: The entites that are in this container
        
        max_bulk: How much place the container has
    """

    dependencies = [Containable]

    def __init__(self):
        Base.__init__(self, children=list, max_bulk=int)
        self.fields["children"].default = list

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        return fields

    @classmethod
    def register(cls, name="container", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Container, cls).register(name, auto_register))

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
        return "Item would exceed the bulk limit of the container."

class NoFreeSlotError(Exception):
    """Error that gets raised when the container has no free slots."""
  
    def __str__(self):
        """Returns the string representing the exception"""
        return "Container can't hold any more items."

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
    container = getattr(container, Container.registered_as)
    index = 0
    for child in container.children:
        if not child:
            return index
        index += 1
    raise NoFreeSlotError

def get_total_bulk(container):
    """Returns the bulk of all items in the container.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        container component
    """
    world = container.world
    container = getattr(container, Container.registered_as)
    total_bulk = 0
    for child in container.children:
        if child:
            child_entity = world.get_entity(child)
            child_component = getattr(child_entity, 
                                      Containable.registered_as)
            total_bulk += child_component.bulk
    return total_bulk

def get_total_weight(container):
    """Returns the weight of all items in the container.
    
    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        container component
    """
    world = container.world
    container = getattr(container, Container.registered_as)
    total_weight = 0
    for child in container.children:
        if child:
            child_entity = world.get_entity(child)
            child_component = getattr(child_entity, 
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
    world = container.world
    container_data = getattr(container, Container.registered_as)
    if type(slot_or_type) == int:
        if len(container_data.children) >= (slot_or_type + 1):
            return world.get_entity(container_data.children[slot_or_type])
    else:
        for child in container_data.children:
            if (child): 
                child_component = getattr(child, Containable.registered_as)
                if (child_component.item_type == slot_or_type):
                    return world.get_entity(child)
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
            container_data.children[item.slot] = None
            item.container = None
            item.slot = -1

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

def put_item(container, item, slot=-1):
    """Puts the item at the given slot in the container and returns the 
    item previously at the slot.

    Args:
        container: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        container component
        
        item: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        containable component
        
        slot: The slot where to pu the item. Defaults to first free slot.

    Raises:
        :class:`fife_rpg.components.container.BulkLimitError` if the item would
        exceed the containers bulk.
    """
    container_data = getattr(container, Container.registered_as)
    item_data = getattr(item, Containable.registered_as)
    if slot == -1:
        slot = get_free_slot(container)
    total_bulk = get_total_bulk(container)
    total_bulk += item_data.bulk
    old_item = get_item(container, slot)
    if old_item:
        old_item_data = getattr(old_item, Containable.registered_as)
        total_bulk -= old_item_data.bulk
    if total_bulk > container_data.max_bulk:
        raise BulkLimitError(total_bulk, container_data.max_bulk)
    remove_item(container, slot)
    container_data.children[slot] = item.identifier
    if item_data.container:
        remove_item(item_data.container, item_data.slot)
    item_data.container = container.identifier
    item_data.slot = slot
    return old_item
