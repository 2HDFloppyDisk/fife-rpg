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

"""The Equip component and functions

.. module:: equip
    :synopsis: The Equip component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base
from fife_rpg.components.equipable import Equipable

class Equip(Base):
    """Basic equipment container component"""
    dependencies = [Equipable]

    def __init__(self, **fields):
        Base.__init__(self, **fields)
    
    @classmethod
    def register(cls, name="equip", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(Equip, cls).register(name, auto_register))

class RPGEquip(Equip):
    """Example component for storing equipped items 
    (what is being worn/wielded)."""

    def __init__(self):
        Equip.__init__(self, head=object, neck=object, body=object, belt=object, 
                      leg=object, feet=object, l_arm=object, r_arm=object)
        self.fields["head"].default = lambda: None
        self.fields["neck"].default = lambda: None
        self.fields["body"].default = lambda: None
        self.fields["belt"].default = lambda: None
        self.fields["leg"].default = lambda: None
        self.fields["feet"].default = lambda: None
        self.fields["l_arm"].default = lambda: None
        self.fields["r_arm"].default = lambda: None

    @classmethod
    def register(cls, name="equip", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(RPGEquip, cls).register(name, auto_register))

class SlotInvalidError(Exception):
    """Error that gets raised when the slot is invalid."""
    
    def __init__(self, slot):
        """Constructor

        Args
            The slot that was found to be invalid
        """
        Exception.__init__(self)
        self.slot = slot
    
    def __str__(self):
        """Returns the string representing the exception"""
        return "\"%s\" is not a valid slot." % self.slot

class AlreadyEquippedError(Exception):
    """Error that gets raised when the equipable already has a wearer"""
    
    def __str__(self):
        """Returns the string representing the exception"""
        return "The equipable is already weared."

class CannotBeEquippedInSlot(Exception):
    """Error that gets raised when the equipable can't be equiped in that 
    slot"""
    
    def __init__(self, slot, equipable):
        """Constructor
        
        Args:
            slot: The slot that was being tried to equip to
            equipable: The item that was being tried to equipped
        """
        Exception.__init__(self)
        self.slot = slot
        self.equipable = equipable
        
    def __str__(self):
        """Returns the string representing the exception"""
        return ("%s is not in the equipables slots. (%s)" % 
                (self.slot, ', '.join(self.equipable.possible_slots))
                )
    
    
def equip(wearer, equipable, slot):
    """Equip the wearer with the given equipable.

    Args:
        wearer: An Entity with a equip component
        equipable: An Entity with a equipable component
        slot: The slot to which the equipable shoud be equipped

    Returns:
        The Entity of the equipable that was at the given slot, or None

    Raises:
        AlreadyEquippedError if the equipable is already equipped elsewhere.
        SlotInvalidError if the slot does not exists
        CannotBeEquippedInSlot if the equipable cannot be equipped in that slot
    """
    wearer_data = getattr(wearer, Equip.registered_as)
    equipable_data = getattr(equipable, Equipable.registered_as)
    if equipable_data.wearer:
        raise AlreadyEquippedError
    if slot in equipable_data.possible_slots:
        try:
            old_item = (getattr(wearer_data, slot)
                        if hasattr(wearer_data, slot) 
                        else None)
            setattr(wearer_data, slot, equipable.identifier)
            equipable_data.in_slot = slot
            equipable_data.wearer = wearer.identifier
            if old_item:
                old_item_entity = wearer.world.get_entity(old_item)
                old_item_data = getattr(old_item_entity, 
                                        Equipable.registered_as)
                old_item_data.in_slot = None
                old_item_data.wearer = None
                return old_item_entity
            return old_item
        except AttributeError:
            raise SlotInvalidError(slot)
    raise CannotBeEquippedInSlot(slot, equipable_data)

def get_equipable(wearer, slot):
    """Return the equipable in the given slot.

    Args:
        wearer: An Entity with a equip component

    Raises:
        SlotInvalidError if there is no such slot
    """
    if not wearer:
        return None
    wearer_data = getattr(wearer, Equip.registered_as)
    try:
        item = getattr(wearer_data, slot)
        return item
    except AttributeError:
        raise SlotInvalidError(slot)
    
def take_equipable(wearer, slot):
    """Remove equipable from the given slot and return it.

    Args:
        wearer: An Equip instance
        slot: The slot from which should be unequipped.
    """
    item = wearer.world.get_entity(get_equipable(wearer, slot))
    wearer_data = getattr(wearer, Equip.registered_as)
    item_data = getattr(item, Equipable.registered_as)
    setattr(wearer_data, slot, None)
    if item_data:
        item_data.in_slot = None
        item_data.wearer = None
    return item
    
    
