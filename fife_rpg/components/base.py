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

"""The base component and functions

.. module:: base
    :synopsis: The base component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from bGrease.component import Component

class Base(Component): # pylint: disable-msg=R0904
    """Base component for fife-rpg."""
    
    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        return self.fields.keys()
