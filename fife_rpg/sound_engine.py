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

# This module was originally taken from the sounds module of PARPG

"""This module holds the object code to play sounds and sound effects

.. module:: __sound_manager
    :synopsis: Holds the object code to play sounds and sound effects

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""


class SoundEngine(object):
    """Plays sounds and __music

    Properties:
        is_music_on: Indicates whether there is currently music playing or not
    """

    def __init__(self, fife_engine):
        """Initialise the SoundEngine instance
           @type fife_engine: fine.Engine
           @param fife_engine: Instance of the Fife __engine
           @return: None"""
        self.__engine = fife_engine
        self.__sound_manager = self.__engine.getSoundManager()
        # self.__sound_manager.init()
        # set up the sound
        self.__music = self.__sound_manager.createEmitter()
        self.__is_music_on = False
        self.__music_init = False

    @property
    def is_music_on(self):
        """Indicates whether there is currently music playing or not"""
        return self.__is_music_on

    def play_music(self, sfile=None):
        """Play music, with the given file if passed

        Args:
            sfile: Filename to play
        """
        if sfile is not None:
            # setup the new sound
            sound = self.__engine.getSoundClipManager().load(sfile)
            self.__music.setSoundClip(sound)
            self.__music.setLooping(True)
            self.__music_init = True
        self.__music.play()
        self.__is_music_on = True

    def pause_music(self):
        """Pauses current music playback"""
        if self.__music_init == True:
            self.__music.pause()
            self.__is_music_on = False

    def toggle_music(self):
        """Toggle status of music, either on or off"""
        if (self.__is_music_on == False) and (self.__music_init == True):
            self.play_music()
        else:
            self.pause_music()

    def set_volume(self, volume):
        """Set the volume of the music

        Args:
           volume: The volume wanted, 0 to 100
        """
        self.__sound_manager.setVolume(0.01 * volume)
