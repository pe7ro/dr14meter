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

import time
import os
import sys
import tempfile
import subprocess
import re
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
        # self.use_ffmpeg = False
        self.__ffmpeg_cmd = get_ffmpeg_cmd()

        if sys.platform.startswith('win'):
            c = self.get_cmd()
            if shutil.which(c):
                self.__cmd = "%s " % self.get_cmd()
            else:
                # todo: fix #5 - is this ever the case?
                print_msg(f'Unable to find "{c}" in PATH, fallback to ".\\decoder\\{c}"')
                self.__cmd = ".\\decoder\\%s " % self.get_cmd()
        else:
            self.__cmd = "%s " % self.get_cmd()

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_ffmpeg_cmd(self):
        return self.__ffmpeg_cmd

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)

    def to_wav(self, file_name):

        full_command = self.__cmd

        (head, file) = os.path.split(file_name)
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join(tmp_dir, file) + ".wav"

        file_name = re.sub(r"(\"|`)", r"\\\1", file_name)
        tmp_file = re.sub(r"(\"|`)", r"_xyz_", tmp_file)

        full_command = full_command + " " + \
            self.get_cmd_options(file_name, tmp_file)

        r = subprocess.Popen(full_command, shell=True,
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout_data, stderr_data = r.communicate()

        if os.path.exists(tmp_file):
            return tmp_file
        else:
            return ""

    def read_audio_file_new(self, file_name, target):

        time_a = time.time()

        full_command = self.__cmd

        (head, file) = os.path.split(file_name)
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join(tmp_dir, file) + ".wav"

        file_name = re.sub(r"(\"|`|\$)", r"\\\1", file_name)
        tmp_file = re.sub(r"(\"|`|\$)", r"_xyz_", tmp_file)

        full_command = full_command + " " + \
            self.get_cmd_options(file_name, tmp_file)

        #print_msg( full_command )

        r = subprocess.Popen(full_command, shell=True,
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout_data, stderr_data = r.communicate()

        #read_wav.read_wav( tmp_file )

        ret_f = self.read_wav(tmp_file, target)

        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        else:
            print_msg(file_name + ": unsupported encoder")
            print_msg(f'Command: {full_command}\nError: {stderr_data}')

        time_b = time.time()
        dr14_log_info(
            "AudioFileReader.read_audio_file_new: Clock: %2.8f" % (time_b - time_a))

        return ret_f

    def read_wav(self, file_name, target):

        time_a = time.time()

        convert_8_bit = numpy.float32(2**8 + 1.0)
        convert_16_bit = numpy.float32(2**15 + 1.0)
        convert_32_bit = numpy.float32(2**31 + 1.0)

        try:
            wave_read = wave.open(file_name, 'r')
            target.channels = wave_read.getnchannels()
            target.Fs = wave_read.getframerate()
            target.sample_width = wave_read.getsampwidth()

            nframes = wave_read.getnframes()
            #print_msg( file_name + "!!!!!!!!!!!!: " + str(target.channels) + " " + str(target.sample_width ) + " " + str( target.Fs ) + " " + str( nframes ) )

            X = wave_read.readframes(wave_read.getnframes())

            sample_type = "int%d" % (target.sample_width * 8)

            target.Y = numpy.fromstring(X, dtype=sample_type).reshape(
                nframes, target.channels)

            wave_read.close()

            if sample_type == 'int16':
                target.Y = target.Y / (convert_16_bit)
            elif sample_type == 'int32':
                target.Y = target.Y / (convert_32_bit)
            else:
                target.Y = target.Y / (convert_8_bit)

            #print_msg( "target.Y: " + str(target.Y.dtype) )
        except:
            self.__init__()
            print_msg("Unexpected error: %s" % str(sys.exc_info()))
            print_msg("\n - ERROR ! ")
            return False

        time_b = time.time()
        dr14_log_info("AudioFileReader.read_wav: Clock: %2.8f" %
                      (time_b - time_a))

        return True

    def get_generic_ffmpeg_options(self, file_name, tmp_file):
        return " -i \"%s\" -b:a 16 -ar 44100 -y \"%s\" -loglevel quiet " % (file_name, tmp_file)


class Mp3FileReader(AudioFileReader):
    pass
    # def get_cmd(self):
    #     ret = "lame"
    #     if check_command(ret):
    #         return ret
    #     else:
    #         self.use_ffmpeg = True
    #
    # def get_cmd_options(self, file_name, tmp_file):
    #     return "--silent " + "--decode " + "\"" + file_name + "\"" + " \"%s\" " % tmp_file



class OggFileReader(AudioFileReader):

    def get_cmd(self):
        return "oggdec"

    def get_cmd_options(self, file_name, tmp_file):
        return "--quiet " + "\"" + file_name + "\"" + " --output \"%s\"  " % tmp_file


class WavFileReader(AudioFileReader):

    def read_audio_file_new(self, file_name, target):
        return self.read_wav(file_name, target)

    def get_cmd(self):
        return ""

    def get_cmd_options(self, file_name, tmp_file):
        return ""

