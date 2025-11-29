#!/usr/bin/python3
import pathlib

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

import subprocess
import sys
import logging
import numpy

from dr14meter.parse_args import parse_args
from dr14meter.dynamic_range_meter import DynamicRangeMeter
from dr14meter.dr14_global import get_exe_name, dr14_version
from dr14meter.dr14_utils import  scan_dir_list, scan_files_list
from dr14meter.out_messages import print_err, print_msg, print_out, set_quiet_msg, init_log
from dr14meter.dr14_config import enable_db, db_is_enabled, database_exists
from dr14meter.database.database import dr_database_singletone
from dr14meter.database.database_utils import enable_database, query_helper, fix_problematic_database, database_exec_query
from dr14meter import dr14_global
from dr14meter import audio_analysis as aa



def run_analysis_opt(options, path_name):
    flag = False

    if options.compress:
        if not dr14_global.test_compress_modules():
            sys.exit(1)
        print_msg("Start compressor:")
        comp = aa.AudioCompressor()
        comp.setCompressionModality(options.compress)
        comp.compute_track(path_name)
        flag = True

    if options.spectrogram:
        if not dr14_global.test_matplotlib_modules("Spectrogram"):
            sys.exit(1)
        print_msg("Start spectrogram:")
        spectr = aa.AudioSpectrogram()
        spectr.compute_track(path_name)
        flag = True

    if options.plot_track:
        if not dr14_global.test_matplotlib_modules("Plot track"):
            sys.exit(1)
        print_msg("Start Plot Track:")
        spectr = aa.AudioPlotTrack()
        spectr.compute_track(path_name)
        flag = True

    if options.plot_track_dst:
        if not dr14_global.test_matplotlib_modules("Plot track dst"):
            sys.exit(1)
        print_msg("Start Plot Track:")
        spectr = aa.AudioPlotTrackDistribution()
        spectr.compute_track(path_name)
        flag = True

    if options.histogram:
        if not dr14_global.test_hist_modules():
            sys.exit(1)
        print_msg("Start histogram:")
        hist = aa.AudioDrHistogram()
        hist.compute_track(path_name)
        flag = True

    if options.lev_histogram:
        if not dr14_global.test_hist_modules():
            sys.exit(1)
        print_msg("Start level histogram:")
        hist = aa.AudioLevelHistogram()
        hist.compute_track(path_name)
        flag = True

    if options.dynamic_vivacity:
        if not dr14_global.test_hist_modules():
            sys.exit(1)
        print_msg("Start Dynamic vivacity:")
        viva = aa.AudioDynVivacity()
        viva.compute_track(path_name)
        flag = True

    return flag


def parse_database_related(options):
    if options.enable_database:
        enable_database()
        return True

    if options.disable_database:
        enable_db(False)
        print_msg("The local DR database is disabled! ")
        return True

    if options.dump_database:
        db = dr_database_singletone().get()
        db.dump()
        return True

    if db_is_enabled():
        db = dr_database_singletone().get()
        f = db.is_db_valid()

        if not f:
            print_err("It seems that there is some problem with the db ... ")
            fix_problematic_database()
            return True

    if options.query is not None:

        if not database_exists():
            print_err("Error: The database does not exist")
            print_err(f"Error: type {get_exe_name} -q for more info.")
            return True

        if len(options.query) == 0:
            query_helper()
            return True

        if options.query[0] not in ["help", "top", "top_alb",
                                    "worst", "worst_alb", "top_art",
                                    "hist", "evol", "codec"]:

            print_err("Error: -q invalid parameter .")
            print_err(f"Error: type {get_exe_name} -q for more info.")
            return True

        table_code = database_exec_query(options)

        if table_code is not None:
            print_out(table_code)

        return True


def main():

    options = parse_args()

    if options.version:
        print_msg(dr14_version())
        return

    init_log(logging.DEBUG)
    logging.disable(logging.INFO)

    numpy.seterr(all='ignore')

    #print( options )

    # everything related to the database functionality
    if parse_database_related(options):
        return

    if options.skip:
        if options.append or options.out_dir is not None or options.turn_off_out:
            options.skip = False

    if options.path_name is not None:
        path_name = pathlib.Path(options.path_name).absolute()
    else:
        path_name = pathlib.Path().absolute()

    if not path_name.exists():
        print_msg(f'Error: The input directory "{path_name}" does not exist!')
        return

    out_dir = pathlib.Path(options.out_dir) if options.out_dir else None
    if out_dir is not None and not out_dir.exists():
        print_msg(f'Error (-o): The target directory "{options.out_dir}"  does not exist!')
        return

    if options.quiet:
        set_quiet_msg()

    # if not options.quiet and not options.skip_version_check:
    #     l_ver = TestVer()
    #     l_ver.start()

    print_msg(path_name)
    print_msg("")

    subdirlist = [path_name]
    if options.recursive:
        subdirlist += [p for p in path_name.rglob('*') if p.is_dir()]

    # utils options
    if run_analysis_opt(options, path_name):
        return 0

    if options.scan_file:
        dr = DynamicRangeMeter()

        dr.write_to_local_db(db_is_enabled())

        r = dr.scan_file(path_name)

        if r == 1:
            print_out("")
            print_out(dr.res_list[0]['file_name'] + " :")
            print_out(f"DR      = {dr.res_list[0]['dr14']}")
            print_out(f"Peak dB = {dr.res_list[0]['dB_peak']:.2f}")
            print_out(f"Rms dB  = {dr.res_list[0]['dB_rms']:.2f}")
            return 0
        else:
            print_msg("Error: invalid audio file")
            return 1

    if options.append and out_dir is None:
        out_dir = path_name

    if options.files_list:
        success, clock, r = scan_files_list(path_name, options, out_dir)
    else:
        success, clock, r = scan_dir_list(subdirlist, options, out_dir)

    if success:
        print_msg("Success!")
        print_msg(f"Elapsed time: {clock:2.2f} sec")
    else:
        print_msg("No audio files found\n")
        print_msg(f" Usage: {get_exe_name()} [options] path_name \n\nfor more details type \n{get_exe_name()} --help\n")

    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        # todo fix:   stty: 'standard input': Inappropriate ioctl for device
        subprocess.run(["stty", "sane"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not success and not database_exists():
        print_msg(" ")
        print_msg(" News ... News ... News ... News ... News  !!! ")
        print_msg(" Now there is the possibility to store all results in a database")
        print_msg(" If you want to enable this database execute the command:")
        print_msg(f"  > {get_exe_name()} --enable_database ")
        print_msg(" for more details visit: http://dr14tmeter.sourceforge.net/index.php/DR_Database ")

    return 0


if __name__ == '__main__':
    print(__file__)

    main()
