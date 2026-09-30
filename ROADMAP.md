# dr14meter roadmap

Where dr14meter is heading: planned changes, ideas for future versions, and known issues.
Nothing here is a promise; items move into a release once someone works on them.

## Direction

- **Correct numbers first.** Results must stay identical to the official offline meter.
  Any change to decoding or measurement is checked against reference results before release.
- **New output format, old one kept.** A future major version gets a new default report
  format; today's format stays available behind a command-line flag.
- **Work with common library layouts** without preprocessing, starting with single-file
  albums + cue sheets.
- **Fail loudly, not wrongly.** Missing tools and unsupported input are reported; one bad
  file or folder does not abort a recursive scan.

## Output format

### Current format (becomes "legacy")

- Text report `dr14-DR<N>.txt` (`-t t`, the default), plus BBCode, HTML and MediaWiki
  (`-t b|h|w`); extended layout by default, basic with `-b`.
- Modelled on the DR logs of the foobar2000 DR meter and the offline meter, so reports could
  be submitted to the DR database at dr.loudness-war.info. `-d/--dr_database` switches the
  header to `Analyzed: <album> / Artist: <artist>`.
- Columns separated by tabs; the console prints `DR = <N>`.

### Plan

- Make the new format the default in 2.0. A flag (name to decide, e.g. `--legacy-format`)
  reproduces the 1.x output byte for byte, so existing scripts keep working.
- Candidate changes, several already prototyped in the arigit fork (see issue #9):
  - columns padded with spaces instead of tabs
  - footer in foobar2000's order: Samplerate, Channels, Bits per sample, Average bitrate, Codec
  - `kbs` → `kbps`
  - console prints `Official DR value: DR<N>` instead of `DR = <N>`
- Machine-readable output (JSON or CSV) for scripts and library tools.

### Open questions

- Does the DR database still accept submissions, and in which format? If not, who still
  depends on the legacy format?
- Does the legacy flag cover all table types, or only the text report?
- Switch the default in 2.0 directly, or ship the new format as opt-in first?

## Planned features

### Single-file album + cue sheet (issue #9)

Merged from arigit/dr14meter (commit `8defcef`), with fixes on top: the image's own tags no
longer override the cue's album/artist, invalid cue sheets fail only their folder, UTF-16 and
cp1252 cue sheets are read, and parallel tracks get unique temp files.

Follow-ups:

- warn when a folder has several cue or audio files (multi-disc) instead of measuring each
  disc as one track; pair cue and audio via the `FILE` line
- `--tag` on cue albums does nothing: skip with a notice, or tag the album DR on the image
- tracks without a `TITLE` show up as `01 - 01 - Album` in the extended report
- cue sheets embedded in FLAC files

### Decode without temporary files

Pipe ffmpeg's output instead of writing a temporary WAV. Use `-f wav` on the pipe and take
channels and sample rate from the header; compute the frame count from the byte length,
since ffmpeg writes a placeholder size on pipes. Don't make decoding depend on ffprobe: the
fork's raw-PCM version assumes stereo when ffprobe is missing and silently gets mono and
5.1 files wrong.

### Automated tests

`tests/sanity-test-00.py` runs the CLI but checks nothing. Add pytest tests on synthetic
audio (numpy + ffmpeg) that assert DR, peak and RMS, plus reference files with known values
from the official meter if we can get them.

## Ideas

- EBU R128 / LUFS loudness next to DR (e.g. via `pyloudnorm` or ffmpeg's `ebur128` filter)
- distinct exit codes: no audio found, ffmpeg missing, invalid path, …
- TOML config instead of the INI `dr14.cfg`
- replace `out_messages.py` with the `logging` module

## Conventions

- New source files start with a one-line license header:
  `# SPDX-License-Identifier: GPL-3.0-or-later`.
  Authors may add their own `# SPDX-FileCopyrightText: <year> <name>` line.
- Existing headers stay as they are; the copyright lines of Simone Riva (dr14_t.meter) and
  other authors are never removed.
- Contributors are credited through git history: merged or cherry-picked commits keep their
  original author, and squashed or reworked code gets a `Co-authored-by:` trailer.

## Known issues

Bugs in the current `master`.

| Problem | Where |
|---|---|
| 24-bit WAV files fail to load (`int24` is not a numpy type) | `audio_file_reader.py` `read_wav` |
| 8-bit WAV is read as signed and scaled by 2^8+1; 8-bit WAV is unsigned and the scale should be 2^7 | `audio_file_reader.py` `read_wav` |
| Non-WAV input is always resampled to 44.1 kHz/16-bit, while WAV is read at its native format | `audio_file_reader.py` `get_cmd_options` |
| Uppercase extensions (`.FLAC`) are skipped | `dynamic_range_meter.py` `scan_mp`, `read_metadata.py` `scan_dir_metadata` |
| A file ffmpeg can't decode raises an uncaught error that aborts the whole run, including `-r` | `audio_file_reader.py` `read_audio_file_new` |
| Writing to the local database crashes: `track_unreadable_failure()` calls `.name` on a string | `read_metadata.py`, `write_dr.py` `write_to_local_dr_database` |
| The Windows line ending is `\n\r` (reversed), and text mode adds another `\r` | `table.py` `Table.nl` |
| Report files use the locale encoding; non-ASCII titles may fail on Windows ("File opening error") | `dynamic_range_meter.py` `fwrite_dr` |
| `ExtendedTextTable`: the title-padding condition is inverted, so separator lines grow with every title (`--query` output) | `table.py` `ExtendedTextTable._update_col_sz` |
| `ExtendedTextTable` `col_cnt` setter: typo `self.col_sz` and swapped branches; more than 5 columns raises AttributeError (`--query`) | `table.py` `ExtendedTextTable.set_col_cnt` |
| `--tag`: `.wav`, `.ac3` and `.wma` raise an exception that aborts the run; `.wv`, `.dsf`, `.dff` and `.oga` aren't supported | `tagger.py` |
| `--compress` writes its result next to the input file, not into the temp directory as intended (the absolute input path wins the path join) | `audio_analysis.py` `AudioCompressor.virt_compute` |
| The config directory is created with `os.mkdir`, which fails if `$XDG_CONFIG_HOME` (or `~/.config`) doesn't exist yet | `dr14_config.py` `get_config_directory` |
