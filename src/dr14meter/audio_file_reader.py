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
import time
import sys
import tempfile
import subprocess
import wave
import numpy
import shutil


from dr14meter.out_messages import print_msg, dr14_log_info
from dr14meter.dr14_global import get_ffmpeg_cmd

#from _ftdi1 import NONE

# ffmpeg -i example.m4a -f wav pipe:1 > test.wav

# def check_command(cmd):
#     try:
#         subprocess.run([cmd, '--version'], check=True, stdout=subprocess.DEVNULL)
#         return True
#     except FileNotFoundError:
#         return False


class AudioFileReader:

    def __init__(self):
        self.__ffmpeg_cmd = get_ffmpeg_cmd()

        if sys.platform.startswith('win'):
            c = self.get_cmd()
            if shutil.which(c):
                self.__cmd = self.get_cmd()
            else:
                print_msg(f'Unable to find "{c}" in PATH')
        else:
            self.__cmd = self.get_cmd()

    def get_cmd(self):
        return self.__ffmpeg_cmd

    def get_cmd_options(self, file_name, tmp_file):
        return [
            '-y',
            '-i',
            file_name,
            *'-b:a 16 -ar 44100'.split(),
            tmp_file,
            '-loglevel', 'quiet',
        ]

    def read_audio_file_new(self, file_name, target):
        file_name = pathlib.Path(file_name)

        time_a = time.time_ns()

        full_command = self.__cmd

        file = file_name.name
        tmp_dir = tempfile.gettempdir()
        tmp_file = pathlib.Path(tmp_dir, file + f"-{time_a}.wav")
        full_command = [full_command] + self.get_cmd_options(file_name, tmp_file)
        subprocess.check_call(full_command, shell=False)
        ret_f = self.read_wav(tmp_file, target)
        tmp_file.unlink(missing_ok=True)

        time_a = time.time_ns() - time_a
        dr14_log_info(f"AudioFileReader.read_audio_file_new: Clock: {time_a / 1000_000_000:2.8f}")

        return ret_f

    def read_wav(self, file_name, target):
        file_name = pathlib.Path(file_name)

        time_a = time.time_ns()

        try:
            with wave.open(str(file_name), 'rb') as wave_read:

                target.channels = wave_read.getnchannels()
                target.Fs = wave_read.getframerate()
                target.sample_width = wave_read.getsampwidth()

                nframes = wave_read.getnframes()
                #print_msg( file_name + "!!!!!!!!!!!!: " + str(target.channels) + " " + str(target.sample_width ) + " " + str( target.Fs ) + " " + str( nframes ) )

                X = wave_read.readframes(wave_read.getnframes())
                sample_type = f"int{target.sample_width * 8}"
                target.Y = numpy.fromstring(X, dtype=sample_type).reshape(nframes, target.channels)

            if sample_type == 'int16':
                convert_16_bit = numpy.float32(2 ** 15 + 1)
                target.Y = target.Y / convert_16_bit
            elif sample_type == 'int32':
                convert_32_bit = numpy.float32(2 ** 31 + 1)
                target.Y = target.Y / convert_32_bit
            else:
                convert_8_bit = numpy.float32(2 ** 8 + 1)
                target.Y = target.Y / convert_8_bit

            #print_msg( "target.Y: " + str(target.Y.dtype) )
        except:
            self.__init__()
            print_msg(f"Unexpected error: {sys.exc_info()}")
            print_msg("\n - ERROR ! ")
            return False

        time_a = time.time_ns() - time_a
        dr14_log_info(f"AudioFileReader.read_wav: Clock: {time_a / 1000_000_000:2.8f}s")

        return True


class WavFileReader(AudioFileReader):

    def read_audio_file_new(self, file_name, target):
        return self.read_wav(file_name, target)

    def get_cmd(self):
        return ""

    def get_cmd_options(self, file_name, tmp_file):
        return ""

