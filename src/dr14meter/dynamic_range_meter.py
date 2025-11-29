# dr14meter: compute the DR14 value of the given audio files
# Copyright (C) 2024  pe7ro
#
# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011 - 2012  Simone Riva
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
import concurrent.futures
import os
import pathlib
import sys

from dr14meter.compute_dr14 import compute_dr14
from dr14meter.audio_track import AudioTrack, StructDuration
from dr14meter.read_metadata import RetrieveMetadata
from dr14meter.write_dr import WriteDr, WriteDrExtended
from dr14meter.audio_math import sha1_track_v1
from dr14meter.dr14_config import get_collection_dir
from dr14meter.dr14_global import min_dr
from dr14meter.out_messages import print_msg, print_out, flush_msg


class DynamicRangeMeter:

    def __init__(self):
        self.res_list = []
        self.dir_name = ''
        self.dr14 = 0
        self.meta_data = RetrieveMetadata()
        self.__write_to_local_db = False
        self.coll_dir = os.path.realpath(get_collection_dir())

    def write_to_local_db(self, f=False):
        self.__write_to_local_db = f

    def scan_file(self, file_name):
        file_name = pathlib.Path(file_name)
        res = run_mp(file_name)
        if not res['fail']:
            self.dr14 = self.dr14 + res['dr14']
            self.res_list.append(res)
        return not res['fail']

    def write_to_local_database(self):

        wr = WriteDr()

        if self.__write_to_local_db and os.path.realpath(self.dir_name).startswith(self.coll_dir):
            wr.write_to_local_dr_database(self)

    def fwrite_dr(self, file_name, tm, ext_table=False, std_out=False, append=False, dr_database=True):

        wr = WriteDrExtended() if ext_table else WriteDr()
        wr.set_loudness_war_db_compatible(dr_database)

        self.table_txt = wr.write_dr(self, tm)

        if std_out:
            print_out(self.table_txt)
            return

        file_mode = "a" if append else "w"
        file_name = pathlib.Path(file_name)

        try:
            with file_name.open(file_mode) as f:  # "utf-8-sig"
                f.write(self.table_txt)
            return True
        except:
            print_msg(f"File opening error [{file_name}]: {sys.exc_info()[0]}")
            return False


    def scan_mp(self, dir_name=None, thread_cnt=None, files_list=None):

        self.dr14 = 0

        if not files_list:
            dir_name = pathlib.Path(dir_name)
            if not dir_name.is_dir():
                return -1
            files_list = sorted(dir_name.glob('*'))
            self.dir_name = str(dir_name)
        else:
            files_list = sorted(pathlib.Path(x) for x in files_list)

        job_queue = [x for x in files_list if x.suffix in AudioTrack.FORMATS]

        if thread_cnt > 1:
            # #6 DR14 Report File Missing Tracks That Appear in Console Output
            # with concurrent.futures.ProcessPoolExecutor(max_workers=thread_cnt) as executor:
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_cnt) as executor:
                results = list(executor.map(run_mp, job_queue))
        else:
            results = [run_mp(x) for x in job_queue]

        # #6 DR14 Report File Missing Tracks That Appear in Console Output
        if len(results) != len(job_queue):
            print_msg(f'Some results were lost: {len(results)} != {len(job_queue)}')

        self.res_list = [x for x in results if not x['fail']]
        # self.res_list = sorted(self.res_list, key=lambda res: res['file_name'])

        succ = 0
        for d in self.res_list:
            if d['dr14'] > min_dr():
                self.dr14 = self.dr14 + d['dr14']
                succ = succ + 1

        self.meta_data.scan_dir_metadata(job_queue)

        if len(self.res_list) > 0 and succ > 0:
            self.dr14 = int(round(self.dr14 / succ))
            return succ
        else:
            return 0

def run_mp(full_file: pathlib.Path, at=None):

    if not at:
        at = AudioTrack()
    duration = StructDuration()

    if at.open(full_file):
        dr14, dB_peak, dB_rms = compute_dr14(at.Y, at.Fs, duration)
        sha1 = sha1_track_v1(at.Y, at.get_file_ext_code())

        print_msg(full_file.name + ": \t DR " + str(int(dr14)))
        flush_msg()

        return {
            'file_name': full_file.name,
            'dr14': dr14,
            'dB_peak': dB_peak,
            'dB_rms': dB_rms,
            'duration': duration.to_str(),
            'sha1': sha1,
            'fail': False,
        }
    else:
        print_msg(f"- fail - {full_file}")
        return {
            'file_name': full_file.name,
            'fail': True,
        }


