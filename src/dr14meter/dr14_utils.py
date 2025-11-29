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


import multiprocessing
import os
import tempfile
import fileinput
import time


from dr14meter import dr14_config as config
from dr14meter.dynamic_range_meter import DynamicRangeMeter #,
from dr14meter.table import TextTable, BBcodeTable, HtmlTable, MediaWikiTable
from dr14meter.out_messages import print_msg


def scan_files_list(input_file, options, out_dir):
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    else:
        out_dir = str(out_dir)

    a = time.time()

    if input_file is None:
        input_file = '-'

    files_list = []

    for line in fileinput.input(input_file):
        files_list.append(os.path.abspath(line.rstrip()))

    dr = DynamicRangeMeter()
    dr.write_to_local_db(config.db_is_enabled())

    cpu = 1 if options.disable_multithread else get_thread_cnt()
    r = dr.scan_mp(files_list=files_list, thread_cnt=cpu)

    if r < 1:
        success = False
    else:
        success = True
        write_results(dr, options, out_dir, "")

    if options.tag:
        from dr14meter.tagger import Tagger
        tagger = Tagger()
        tagger.write_dr_tags(dr)


    clock = time.time() - a
    return success, clock, r


def scan_dir_list(subdirlist, options, out_dir):
    a = time.time()

    success = False
    r = 0

    for cur_dir in subdirlist:
        print_msg("\n------------------------------------------------------------ ")
        if options.skip:
            x = list(cur_dir.glob('dr14*.txt'))
            if len(x) > 0:
                print_msg(f'# Skipping "{cur_dir}", because {[a.name for a in x]} found.')
                continue
        dr = DynamicRangeMeter()
        dr.write_to_local_db(config.db_is_enabled())

        print_msg(f"> Scan Dir: {cur_dir} \n")

        cpu = 1 if options.disable_multithread else get_thread_cnt()
        r = dr.scan_mp(cur_dir, cpu)

        if options.tag:
            from dr14meter.tagger import Tagger
            tagger = Tagger()
            tagger.write_dr_tags(dr)

        if r < 1:
            continue
        else:
            success = True

        write_results(dr, options, out_dir, cur_dir)

    clock = time.time() - a

    return success, clock, r


def get_thread_cnt():
    cpu = multiprocessing.cpu_count()
    cpu = max(2, int(round(cpu / 2)))
    return cpu


def write_results(dr, options, out_dir, cur_dir):
    table_format = not options.basic_table

    full_out_dir = os.path.join(cur_dir) if out_dir is None else out_dir

    print_msg("DR = " + str(dr.dr14))

    if not (os.access(full_out_dir, os.W_OK)):
        full_out_dir = tempfile.gettempdir()
        print_msg("--------------------------------------------------------------- ")
        print_msg("- ATTENTION !")
        print_msg("- You do not have the write permission for the directory: %s " % full_out_dir)
        print_msg("- The result files will be written in the tmp dir: %s " % full_out_dir)
        print_msg("--------------------------------------------------------------- ")

    if options.print_std_out:
        dr.fwrite_dr("", TextTable(), table_format, std_out=True)

    if options.turn_off_out:
        return

    all_tables = False
    if 'a' in options.out_tables:
        all_tables = True

    tables_list = {
        'b': ["dr14_bbcode.txt", BBcodeTable()],
        't': ["dr14-DR"+str(dr.dr14)+".txt",TextTable()],
        'h': ["dr14.html", HtmlTable()],
        'w': ["dr14_mediawiki.txt", MediaWikiTable()]
    }

    out_list = ""

    dr.write_to_local_database()

    for code in tables_list.keys():
        if code in options.out_tables or all_tables:
            dr.fwrite_dr(os.path.join(full_out_dir, tables_list[code][0]), tables_list[code][1], table_format,
                         append=options.append, dr_database=options.dr_database)
            out_list += " %s " % tables_list[code][0]

    print_msg("")
    print_msg("- The full result has been written in the files: %s" % out_list)
    print_msg("- located in the directory: ")
    print_msg(full_out_dir)
    print_msg("")


def test_path_validity(path):
    if path in ["/", ""]:
        return False
    if os.access(path, os.W_OK):
        return True
    else:
        (h, t) = os.path.split(path)
        return test_path_validity(h)


