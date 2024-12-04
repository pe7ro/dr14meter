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
import subprocess

from dr14meter.out_messages import print_msg


lock_ver = threading.Lock()

ffmpeg_cmd = None


def dr14_version():
    try:
        return importlib.metadata.version('dr14meter')
    except ModuleNotFoundError:
        print_msg("The %s function require the installation of MatPlotLib")
    return 'UNDEF'


def min_dr():
    return -10000


def get_exe_name():
    return "dr14meter"


def get_name_version():
    return f'dr14meter {dr14_version()}'


def get_ffmpeg_cmd():

    global ffmpeg_cmd

    if ffmpeg_cmd == None:
        ffmpeg_f = subprocess.call(
            "type " + "ffmpeg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
        avconv_f = subprocess.call(
            "type " + "avconv", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

        if ffmpeg_f:
            ffmpeg_cmd = "ffmpeg"
        elif avconv_f:
            ffmpeg_cmd = "avconv"

    return ffmpeg_cmd


def get_home_url():
    return "https://github.com/pe7ro/p7_dr14meter"


def test_matplotlib_modules(fun_name):
    try:
        import matplotlib
    except ImportError:
        print_msg(
            "The %s function require the installation of MatPlotLib: http://matplotlib.sourceforge.net" % fun_name)
        return False

    return True

def test_mutagen(fun_name):
    try:
        import mutagen
    except ImportError:
        print_msg(
            "The %s function require the installation of MatPlotLib: http://matplotlib.sourceforge.net" % fun_name)
        return False

    return True

def test_hist_modules():
    try:
        import matplotlib
    except ImportError:
        print_msg(
            "The histogram function require the installation of MatPlotLib: http://matplotlib.sourceforge.net")
        return False

    return True


def test_compress_modules():
    try:
        import scipy
    except:
        print_msg(
            "The compression function require the installation of SciPy: http://www.scipy.org/")
        return False

    return True
