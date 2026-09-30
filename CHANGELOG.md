# Changelog

Notable changes in each release. Versions up to 1.0.16 were released as
[dr14_t.meter](https://github.com/simon-r/dr14_t.meter) by Simone Riva.

## Unreleased

- Added automated tests (`python -m pytest`, see `INSTALL.md`).
- README: short installation, usage and license sections.
- Removed the man page (`man/`). It was outdated and wasn't installed by pip or pipx;
  `dr14meter --help` lists all options.
- Fixed `--compress` crashing with numpy 2 (`ndarray.tostring` was removed).
- Fixed `--plot_track_dst` crashing on mono files and drawing the second channel in every plot.
- Fixed the local database: two albums by a new artist in one run crashed the insert, and an
  error during a write left a lock held so later writes hung. Connections are now closed.
- The exit code is 1 when the input path or the `-o` directory doesn't exist, and
  `python -m dr14meter` now returns the exit code too.
- `--compress` no longer prints debug values to stdout; `--plot_track` and `--spectrogram` no
  longer use the deprecated `pylab` module.

## 1.1.6 — 2026-09-30

- Added support for single-file albums with a cue sheet: a folder with exactly one audio file
  and one `.cue` is measured per track, as the cue sheet describes (#9, thanks arigit).
- Added `ROADMAP.md`: planned changes, conventions and known issues.
- Removed the Debian packaging (`debian/`). It was outdated and could no longer be built;
  install with `pipx install dr14meter` (see `INSTALL.md`). Its release history is kept below.

## 1.1.5 — 2025-11-29

- Added `--skip`: ignore folders that already contain a `dr14*` report.
- Tracks are scanned in threads instead of processes, so the report no longer misses
  tracks shown in the console (#6).
- Ogg files are decoded with ffmpeg; `oggdec` is no longer needed.
- Fixed a crash with numpy 2.3+, which removed `numpy.fromstring` (#7, thanks tnpapa).
- mutagen is only imported when `--tag` is used.
- The exit code is 0 on success (it used to be the number of scanned files).
- Code cleanup and documentation updates.

## 1.1.4 — 2025-02-10

- Fixed ffmpeg not being found in PATH on Windows (#5).
- Removed avconv/avprobe support and Python 2 code.

## 1.1.3 — 2025-01-30

- Fixed ffmpeg not being found on Windows (#4).
- Minor metadata fix; fixed links in the README.

## 1.1.2 — 2024-12-19

- Fixed the "unsupported encoder" error with mp3 files (#3).
- Fixed an exception in `--plot_track` (#2).
- Moved the database and plotting code into subpackages; removed duplicate code.

## 1.1.1 — 2024-12-05

- Fixed `--spectrogram`, `--plot_track_dst`, `--lev_hist` and `--dyn_vivacity`.

## 1.1.0 — 2024-12-04

First release as dr14meter.

- Renamed the package to `dr14meter` and published it on PyPI; switched from `setup.py`
  to `pyproject.toml`; removed the online version check.
- The report states explicitly when tracks have different sample rates or bit depths.
- Fixed `--hist` (#1).
- Includes the dr14_t.meter work that was never released after 1.0.16: a local DR database
  with queries (`--enable_database`, `-q`, `--dump_database`), Opus, WavPack and DSD
  (`.dsf`, `.dff`) support, the `--tag` option, correct bit depth for 24-bit FLAC, a fix for
  the inverted `-d/--dr_database` flag, XDG config directory support, and Python 3 as the
  default interpreter.

## 1.0.16 — 2015-01-02

- Bug fix.

## 1.0.15 — 2014-11-25

- Added avconv and AC3 support.

## 1.0.14 — 2013-11-17

- Fixed a problem on macOS.

## 1.0.13 — 2013-04-27

- Use the Linux-style command on every non-Windows platform.

## 1.0.12 — 2012-11-26

- Fixed an encoding problem in quiet mode and a problem with unusual tracks
  (dr14_t.meter issues 9 and 10).

## 1.0.11 — 2012-10-28

- Fix for Python 3.3.

## 1.0.10 — 2012-09-23

- Added the track plot with zoom and scroll.

## 1.0.5 — 2012-09-12

- Much faster computation; fixed UTF-8 file names with Python 2.

## 1.0.0 — 2012-09-07

- 24-bit audio support.
- New features: dynamic compressor, spectrogram, level histogram, dynamic vivacity graph,
  file list scanning, quiet mode.

## 0.9.5 — 2012-08-20

- scipy is no longer required; added the dynamic histogram (beta).

## 0.9.0 — 2012-08-10

- Output compatible with the DR database, multi-core computing by default, MediaWiki table.

## 0.8.5 — 2012-02-17

- Bug fix.

## 0.8.4 — 2012-02-16

- Bug fix.

## 0.8.3 — 2012-02-13

- Options to skip writing the output file and to print the result on the console.

## 0.8.2 — 2012-02-09

- Fixed the extended table output and the track number layout.

## 0.8.1 — 2012-02-02

- Recursive scan; fixes.

## 0.8.0 — 2012-01-20

- ALAC support; extended table format.

## 0.7.3 — 2012-01-02

- Track duration, online test version, improved output tables.

## 0.6.0 — 2011-12-16

- Initial release.
