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

import sys
import os
import logging
import codecs

message_file = sys.stderr
out_file = sys.stdout
err_file = sys.stderr
mode = "verbose"

logger = logging.getLogger('dr14log')


def init_log(level=logging.DEBUG):
    global logger

    logger = logging.getLogger('dr14log')

    stream_h = logging.StreamHandler()
    stream_h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    stream_h.setLevel(level)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_h)


def dr14_log_debug(message):
    global logger
    logger.debug(message)


def dr14_log_info(message):
    global logger
    logger.info(message)

########


def print_msg(string):
    global message_file
    message_file.write(f"{string}\n")


def flush_msg():
    global message_file
    message_file.flush()


def print_err(string):
    global err_file
    err_file.write(f"Error: {string} \n")


def flush_err():
    global message_file
    err_file.flush()


def print_out(string):
    global out_file
    out_file.write(f"{string}\n")


def flush_out():
    global message_file
    out_file.flush()


def set_verbose_msg():
    global message_file
    global mode

    if mode == "verbose":
        return

    codecs.close(message_file)

    message_file = sys.stderr


def set_quiet_msg():
    global message_file
    global mode

    if mode == "quiet":
        return

    message_file = open(os.devnull, "w")
