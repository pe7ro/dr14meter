# dr14meter: compute the DR14 value of the given audio files
# Copyright (C) 2024  pe7ro
#
# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from dr14meter import dr14_global
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TXXX
from dr14meter.audio_file_reader import *


class Tagger:

    FORMATS = ['.flac', '.mp3', '.ogg', '.opus', '.mp4', '.m4a', '.wav', '.ape', '.ac3', '.wma']

    def __init__(self):
        # fixme can it lead to '/filename' as a path in update_track_tags ?
        self.dir_name = ''
        self._ext = -1
    
    def write_dr_tags(self, dr):

        if not dr14_global.test_mutagen("Tagging"):
            sys.exit(1)

        self.dir_name = dr.dir_name
        
        for item in dr.res_list:
            self.update_track_tags(item)

    def get_file_ext_code(self):
        return self._ext

    def update_track_tags(self, item):

        (f, ext) = os.path.splitext(item['file_name'])
        ext = ext.lower()

        if ext not in Tagger.FORMATS:
            return False

        filename = self.dir_name + os.sep + item['file_name']

        if ext == '.mp3':
            audio = MP3(filename)
            # audio.add_tags
        elif ext == '.flac':
            audio = FLAC(filename)
        elif ext == '.ogg':
            audio = OggVorbis(filename)
        elif ext == '.opus':
            audio = OggOpus(filename)
        elif ext in ['.mp4', '.m4a']:
            audio = MP4(filename)
        elif ext == '.ape':
            audio = MonkeysAudio(filename)
        else:
            # wma ac3 wav
            raise Exception(f"Tagging {ext} files not supported")

        if isinstance(audio, MP3):
            audio.tags.add(TXXX(encoding=3, desc=u"DR", text=[str(item["dr14"])]))
        else:
            audio["DR"] = [str(item["dr14"])]
        
        audio.save()
        self._ext = Tagger.FORMATS.index(ext)
        return True