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

from base import Base

class Equip(Base):
    """
    Component that stores the equipment (what is being worn/wielded).
    """
    
    def __init__(self):
        Base.__init__(self, head=object, neck=object, body=object, belt=object, 
                      leg=object, feet=object, l_arm=object, r_arm=object)
        self.head = None
        self.neck = None
        self.body = None
        self.belt = None
        self.leg = None
        self.feet = None
        self.l_arm = None
        self.r_arm = None

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        return []

class SlotInvalidError(Exception):
    """Error that gets raised when the slot is invalid."""
    
    def __init__(self, slot):
        """Constructor

        Args
            The slot that was found to be invalid
        """
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
        wearer: An Equip instance
        equipable: An Equipable instance
        slot: The slot to which the equipable shoud be equipped

    Returns:
        The equipable that was at the given slot, or None

    Raises:
        AlreadyEquippedError if the equipable is already equipped elsewhere.
        SlotInvalidError if the slot does not exists
        CannotBeEquippedInSlot if the equipable cannot be equipped in that slot
    """
    if equipable.wearer:
        raise AlreadyEquippedError
    if slot in equipable.possible_slots:
        try:
            old_item = getattr(wearer, slot) if hasattr(wearer, slot) else None
            setattr(wearer, slot, equipable)
            equipable.in_slot = slot
            equipable.wearer = wearer
            if old_item:
                old_item.in_slot = None
                old_item.wearer = None
            return old_item
        except AttributeError:
            raise SlotInvalidError(slot)
    raise CannotBeEquippedInSlot(slot, equipable)

def get_equipable(wearer, slot):
    """Return the equipable in the given slot.

    Raises:
        SlotInvalidError if there is no such slot
    """
    if not wearer:
        return None
    try:
        item = getattr(wearer, slot)
        return item
    except AttributeError:
        raise SlotInvalidError(slot)
    
def take_equipable(wearer, slot):
    """Remove equipable from the given slot and return it.

    Args:
        wearer: An Equip instance
        slot: The slot from which should be unequipped.
    """
    item = get_equipable(wearer, slot)
    setattr(wearer, slot, None)
    if item:
        item.in_slot = None
        item.wearer = None
    return item
    
    
