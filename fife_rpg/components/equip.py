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
    """Basic equipment container component
    
    Fields:
        Slots are dynamically set on construction
    """
    dependencies = [Equipable]

    def __init__(self, **fields):
        """Create the slots.
        
        Args:
            fields: kwargs argument containing the data of the fields
        """
        Base.__init__(self, **fields)
    
    @classmethod
    def register(cls, name="Equip", auto_register=True):
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
    (what is being worn/wielded).
    
    Fields:
        head: Head equipment slot
        neck: Neck equipment slot
        body: Body equipment slot
        belt: Belt equipment slot
        leg: Legs equipment slot
        feet: Feet equipment slot
        l_arm: Left arm equipment slot
        r_arm: Right arm equipment slot
    """

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
    """Error that gets raised when the slot is invalid

    Properties:
        The slot that was found to be invalid
    """
    
    def __init__(self, slot):
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
    slot
    
    Properties:
        slot: The slot that was being tried to equip to
        
        equipable: The item that was being tried to equipped
    """
    
    
    def __init__(self, slot, equipable):
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
        wearer: An :class:`fife_rpg.entites.rpg_entity.RPGEntity` with a
        equip component
        
        equipable: An :class:`fife_rpg.entites.rpg_entity.RPGEntity` with a
        equipable component
        
        slot: The slot to which the equipable shoud be equipped

    Returns:
        The Entities of the equipable that had to be unqeuipped, or None

    Raises:
        :class:`fife_rpg.components.equip.AlreadyEquippedError` if the
        equipable is already equipped elsewhere.
        
        :class:`fife_rpg.components.equip.SlotInvalidError` if the slot
        does not exists
        
        :class:`fife_rpg.components.equip.CannotBeEquippedInSlot` if the
        equipable cannot be equipped in that slot
    """
    wearer_data = getattr(wearer, Equip.registered_as)
    equipable_data = getattr(equipable, Equipable.registered_as)
    if equipable_data.wearer:
        raise AlreadyEquippedError
    for possible_slots in equipable_data.possible_slots:
        possible_slots = possible_slots.split(",")
        if slot in possible_slots:
            try:
                old_items = []
                if isinstance(possible_slots, str):
                    possible_slots = [possible_slots]
                for possible_slot in possible_slots:
                    old_item = (getattr(wearer_data, possible_slot)
                                if hasattr(wearer_data, possible_slot) 
                                else None)
                    setattr(wearer_data, slot, equipable.identifier)
                    if old_item:
                        old_item_entity = wearer.world.get_entity(old_item)
                        old_item_data = getattr(old_item_entity, 
                                                Equipable.registered_as)
                        old_item_data.in_slot = None
                        old_item_data.wearer = None
                        old_items.append(old_item_entity)

                equipable_data.in_slot = ",".join(possible_slots)
                equipable_data.wearer = wearer.identifier
                return old_items
            except AttributeError:
                raise SlotInvalidError(slot)
    raise CannotBeEquippedInSlot(slot, equipable_data)

def get_equipable(wearer, slot):
    """Return the equipable in the given slot.

    Args:
        wearer: An :class:`fife_rpg.entites.rpg_entity.RPGEntity`
        with a equip component

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
        wearer: An :class:`fife_rpg.components.equip.Equip` instance
        
        slot: The slot from which should be unequipped.
    """
    item = wearer.world.get_entity(get_equipable(wearer, slot))
    wearer_data = getattr(wearer, Equip.registered_as)
    item_data = getattr(item, Equipable.registered_as)
    if isinstance(item_data.in_slot, str):
        setattr(wearer_data, slot, None)
    else:     
        for in_slot in item_data.in_slot:
            setattr(wearer_data, in_slot, None)
    if item_data:
        item_data.in_slot = None
        item_data.wearer = None
    return item
    
    
