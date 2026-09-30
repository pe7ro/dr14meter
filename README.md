dr14meter is a command-line tool for computing the dynamic range of your music, following the procedure described by the Pleasurize Music Foundation. 

It is based on [simon-r/dr14_t.meter](https://github.com/simon-r/dr14_t.meter) which has not been updated for a while now.
The goal is to provide bugfixes and occasional updates to the tool.

For more info visit: <https://github.com/pe7ro/dr14meter>

Installation packages available at pypi: <https://pypi.org/project/dr14meter/>

### Installation ###

dr14meter needs [ffmpeg](https://ffmpeg.org/) (with `ffprobe`) in your PATH.

```bash
pipx install dr14meter
# with the optional plots (--hist, --spectrogram, ...) and tagging (--tag):
pipx install "dr14meter[plot,tagging]"
```

Installing from source: see [INSTALL.md](https://github.com/pe7ro/dr14meter/blob/master/INSTALL.md).

### Usage ###

```bash
dr14meter /path/to/album          # scan a folder; writes dr14-DR<N>.txt into it
dr14meter -r /path/to/music       # scan all subfolders too
dr14meter -f /path/to/track.flac  # a single file
dr14meter --help                  # all options
```

A folder with a single audio file and a `.cue` sheet is measured per track, as the cue sheet describes.

### License ###

GPL-3.0-or-later, see [LICENSE](https://github.com/pe7ro/dr14meter/blob/master/LICENSE).
Based on [dr14_t.meter](https://github.com/simon-r/dr14_t.meter) by Simone Riva.

### Introduction to DR14 T.meter ###

DR14 T.meter is a free and open source command line tool for computing the Dynamic Range of your music 
according to the procedure used in the off-line meter released by the Pleasurize Music Foundation. 
[Link to the procedure's definition in PDF article](http://www.dynamicrange.de/sites/default/files/Measuring%20DR%20ENv3.pdf)
or
[from web archive](https://web.archive.org/web/20180917133436/http://www.dynamicrange.de/sites/default/files/Measuring%20DR%20ENv3.pdf)

This tool is very useful to measure how is loud your music and for understanding that a good quality album 
always has also a good dynamic, and it's also useful for understanding the effects of the so called loudness war.

Dr14 t.meter is released under the terms of the  GNU GPLv3 license and  is intended for the Linux users 
that can not use the Windows application released by the Pleasurize Music Foundation or the plugin for Foobar2000.

It is largely tested and has always returned results identical to those of the official off-line meter.

