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

import pathlib
import numpy
from dr14meter.audio_decoder import AudioDecoder


class AudioTrack:

    def __init__(self):
        self.Y = numpy.array([])
        # e.g. 44100
        self.Fs = 0
        self.channels = 0
        self.sample_width = 0
        self._ext = -1
        self._de = AudioDecoder()

    def time(self):
        return 1 / self.Fs * self.Y.shape[0]

    def get_file_ext_code(self):
        return self._ext

    def open(self, file_name: pathlib.Path):
        file_name = pathlib.Path(file_name)

        self.Y = numpy.array([])
        self.Fs = 0
        self.channels = 0

        if not file_name.exists():
            return False

        res_f = self._de.read_track_new(file_name, self)
        self._ext = self._de.get_file_ext_code()

        return res_f


class StructDuration:

    def __init__(self):
        self.tm_min = 0
        self.tm_sec = 0

    def set_samples(self, samples, Fs):
        self.tm_min, self.tm_sec = divmod(int(samples * (1.0 / Fs)), 60)

    def to_str(self):
        return str(self.tm_min) + ":%02d" % int(self.tm_sec)
