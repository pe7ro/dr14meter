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

import importlib.metadata
import threading
import shutil

from dr14meter.out_messages import print_msg


lock_ver = threading.Lock()

ffmpeg_cmd = None


def dr14_version():
    try:
        return importlib.metadata.version('dr14meter')
    except ModuleNotFoundError:
        print_msg("Unable to get the version of the app")
    return 'UNDEF'


def min_dr():
    return -10000


def get_exe_name():
    return "dr14meter"


def get_name_version():
    return f'dr14meter {dr14_version()}'


def get_ffmpeg_cmd():

    global ffmpeg_cmd

    if ffmpeg_cmd is not None:
        return ffmpeg_cmd

    if not shutil.which('ffmpeg'):
        print_msg('ffmpeg not found in PATH')
    ffmpeg_cmd = 'ffmpeg'
    return ffmpeg_cmd


def get_home_url():
    return "https://github.com/pe7ro/dr14meter"


def test_lib(lib_name, fun_name):
    try:
        # __import__(lib_name)
        importlib.import_module(lib_name)
    except ImportError:
        print_msg(f"The {fun_name} function require the installation of {lib_name}")
        return False

    return True


def test_matplotlib_modules(fun_name):
    return test_lib('matplotlib', fun_name)


def test_mutagen(fun_name):
    return test_lib('mutagen', fun_name)


def test_hist_modules():
    return test_lib('matplotlib', 'histogram')


def test_compress_modules():
    return test_lib('scipy', 'compression')

