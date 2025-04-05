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

import collections
import pathlib
import subprocess
import re
import hashlib
import numpy as np

from dr14meter.audio_track import AudioTrack
from dr14meter.dr14_global import get_ffmpeg_cmd


def match_repetitive_title(data_txt):
    m = re.search(r"(\S[\S ]+\S)\s*;\s*\1", data_txt, RetrieveMetadata.re_flags)
    return data_txt if m is None else m.group(1)

class UnreadableAudioFileException(Exception):
    pass


class RetrieveMetadata:
    re_flags = (re.MULTILINE | re.IGNORECASE | re.UNICODE)

    def __init__(self):
        self._album = collections.defaultdict(int)
        self._artist = collections.defaultdict(int)
        self._tracks = {}
        self._disk_nr = []

        # print a warning if ffmpeg not found
        get_ffmpeg_cmd()
        self.__ffprobe_cmd = "ffprobe"

    def scan_dir_metadata(self, files_path_list):

        self._album = collections.defaultdict(int)
        self._artist = collections.defaultdict(int)
        self._tracks = {}
        self._disk_nr = []

        # if files_path_list is None:
        #     files_path_list = sorted(dir_name.glob('*'))

        for file_path in files_path_list:
            if file_path.suffix in AudioTrack.FORMATS:
                try:
                    self.scan_file_orig(file_path)
                except UnreadableAudioFileException as uafe:
                    pass


    def scan_file_orig(self, file_path: pathlib.Path):

        try:
            cmd = [self.__ffprobe_cmd, "-show_format", "-show_streams", file_path]
            data_txt = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
        except:
            self._tracks[file_path.name] = None
            raise UnreadableAudioFileException(f"problematic file: {file_path}")

        try:
            data_txt = data_txt.decode(encoding='UTF-8')
        except:
            data_txt = data_txt.decode(encoding='ISO-8859-1')

        track = {'file_name': file_path.name}

        pattern = r"[ \t\f\v]*([\S \t\f\v]+\S).*$"

        # default (album) fields

        m = re.search(r"^\s*album\s*\:" + pattern, data_txt, RetrieveMetadata.re_flags)
        if m is not None:
            track['album'] = match_repetitive_title(m.group(1))
            self._album[track['album']] += 1

        m = re.search(r"^\s*artist\s*\:" + pattern, data_txt, RetrieveMetadata.re_flags)
        if m is not None:
            track['artist'] = match_repetitive_title(m.group(1))
            self._artist[track['artist']] += 1

        # repetitive fields

        m = re.search(r"^\s*title\s*\:" + pattern, data_txt, RetrieveMetadata.re_flags)
        if m is not None:
            track['title'] = match_repetitive_title(m.group(1))


        m = re.search(r"^\s*genre\s*\:" + pattern, data_txt, RetrieveMetadata.re_flags)
        if m is not None:
            track['genre'] = match_repetitive_title(m.group(1))

        # simple tags

        simple_tags = [
            ('track_nr', r"^\s*track\s*\:\s*(\d+).*$", int),
            ('date', r"^\s*date\s*\:\s*(\d+).*$", str),
            ('disk_nr', r"^\s*disc\s*:\s*(\d+).*$", int),
            ('size', r"^size=\s*(\d+)\s*$", str),
            ('bitrate', r"^bit_rate=\s*(\d+)\s*$", str),
            ('duration', r"^duration=\s*(\d+\.\d+)\s*$", float),
        ]

        for t, p, f in simple_tags:
            m = re.search(p, data_txt, RetrieveMetadata.re_flags)
            if m is not None:
                track[t] = f(m.group(1))

        self.__read_stream_info(data_txt, track)
        self._tracks[file_path.name] = track


    def __read_stream_info(self, data_txt, track):


        ##########################################
        # string examples:
        # Audio: flac, 44100 Hz, stereo, s16
        # Stream #0:0(und): Audio: alac (alac / 0x63616C61), 44100 Hz, 2 channels, s16, 634 kb/s
        # Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 255 kb/s (default
        # Stream #0:0: Audio: flac, 44100 Hz, stereo, s16

        m = re.search(r"Stream.*Audio:(.*)$", data_txt, RetrieveMetadata.re_flags)
        if m != None:
            fmt = m.group(1)

        fmt = re.split(",", fmt)

        #print( fmt )
        track['codec'] = re.search(r"\s*(\w+)", fmt[0], RetrieveMetadata.re_flags).group(1)
        track['sampling_rate'] = re.search(
            r"\s*(\d+)", fmt[1], RetrieveMetadata.re_flags).group(1)
        track['channel'] = re.search(
            r"^\s*([\S][\s|\S]*[\S])\s*$", fmt[2], RetrieveMetadata.re_flags).group(1)

        m = re.search(r"\((\d+) bit\)", fmt[3], RetrieveMetadata.re_flags)
        if m != None:
            track['bit'] = m.group(1)
        else:
            m = re.search(r"(\d+)", fmt[3], RetrieveMetadata.re_flags)
            if m != None:
                track['bit'] = m.group(1)
            else:
                track['bit'] = "16"

    def album_len(self):
        return len(self._tracks)

    def get_album_cnt(self):
        return len(self._album)

    def get_disk_nr(self):
        # fixme return all disk numbers?
        if len(self._disk_nr) > 0:
            return self._disk_nr[0]
        else:
            return None

    def get_album_list(self):
        return self._album

    def get_album_title(self):

        if len(self._album) > 1:
            return "Various"
        elif len(self._album) == 0:
            return None
        else:
            return collections.Counter(self._album).most_common(1)[0][0]

    def track_unreadable_failure(self, file_path):
        return file_path.name not in self._tracks

    def get_album_sha1(self, title=None):

        if title is None:
            p_title = self.get_album_title()
        else:
            p_title = title

        str_conv = str

        key_string = str_conv("")
        #key_string = key_string + str_conv( p_title ) + str_conv( self.get_album_artist() )

        d = np.float64(0.0)
        s = np.float64(0.0)

        for track in sorted(self._tracks.keys()):

            if self._tracks[track] == None:
                continue

            if not self._tracks[track].get('size', False) or not self._tracks[track].get('codec', False):
                continue

            if title != None and not self._tracks[track]["album"] != title:
                continue

            #key_string = key_string + str_conv( track )
            key_string = key_string + str_conv(self._tracks[track]['size'])
            key_string = key_string + str_conv(self._tracks[track]['codec'])
            key_string = key_string + str_conv(self._tracks[track]['duration'])
            key_string = key_string + \
                str_conv(int(self._tracks[track]['bitrate']))
            d += np.float64(self._tracks[track]['duration'])
            s += np.float64(self._tracks[track]['size'])

        key_string = key_string + str_conv(d)
        key_string = key_string + str_conv(s)

        sa = np.frombuffer(bytearray(key_string.encode("utf8")), dtype=np.int8)

        #print( np.sum( sa ) )
        #print( len( sa ) )
        #print( len(key_string) )

        #print( bytearray( key_string.encode("utf8") ) )

        sha1 = hashlib.sha1(sa).hexdigest()
        #print( sha1 )
        return sha1

    def get_album_artist_old(self):

        if len(self._artist) > 1:
            return "Various Artists"
        elif len(self._artist) == 0:
            return None
        else:
            for k in self._artist.keys():
                res = k
            return res

    def get_album_artist(self, album=None):

        if album is None:
            return [self.get_album_artist_old()]

        artists = []
        for track in self._tracks.keys():
            if track["album"] == album:
                if not track["artist"] in artists:
                    artists.append(track["artist"])

        return artists

    def get_value(self, file_name: str, field):
        f = self._tracks.get(file_name, None)
        if f is None:
            return None
        return f.get(field, None)


