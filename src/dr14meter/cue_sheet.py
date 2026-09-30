# SPDX-License-Identifier: GPL-3.0-or-later

import codecs
import pathlib
import re


class CueParseError(Exception):
    pass


def _parse_index_time(time_str):
    """Convert a cue MM:SS:FF timestamp (FF = 1/75th of a second frames) to seconds."""
    m = re.match(r'^(\d+):(\d+):(\d+)$', time_str)
    if not m:
        raise CueParseError(f"Invalid INDEX time: {time_str}")
    mm, ss, ff = (int(x) for x in m.groups())
    return mm * 60 + ss + ff / 75.0


def _unquote(value):
    value = value.strip()
    m = re.match(r'^"(.*)"$', value)
    return m.group(1) if m else value


class CueSheet:
    """Minimal parser for a single-FILE cue sheet: enough to split one audio
    file into the track time ranges it describes."""

    _LINE_RE = re.compile(r'^(\S+)\s*(.*)$')

    def __init__(self, cue_path: pathlib.Path):
        self.cue_path = pathlib.Path(cue_path)
        self.album_title = None
        self.album_performer = None
        self.genre = None
        self.date = None
        self.audio_file_ref = None
        self.tracks = []

        self._parse(self._read_text())

    def _read_text(self):
        data = self.cue_path.read_bytes()

        # EAC and others write UTF-16 cue sheets with a BOM; otherwise try UTF-8
        # (with or without BOM), then cp1252, the usual Windows encoding.
        # latin-1 maps every byte, so it is the last resort.
        if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            encodings = ('utf-16',)
        else:
            encodings = ('utf-8-sig', 'cp1252', 'iso-8859-1')

        for enc in encodings:
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        raise CueParseError(f"Unable to decode cue sheet {self.cue_path}")

    def _parse(self, text):
        cur_track = None
        file_cnt = 0

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            m = self._LINE_RE.match(line)
            if not m:
                continue

            cmd, rest = m.group(1).upper(), m.group(2).strip()

            if cmd == 'REM':
                sub_m = self._LINE_RE.match(rest)
                if sub_m:
                    key, val = sub_m.group(1).upper(), _unquote(sub_m.group(2))
                    if key == 'GENRE':
                        self.genre = val
                    elif key == 'DATE':
                        self.date = val

            elif cmd == 'FILE':
                file_cnt += 1
                fm = re.match(r'^"(.*)"', rest)
                self.audio_file_ref = fm.group(1) if fm else (rest.split() or [None])[0]

            elif cmd == 'TRACK':
                tm = re.match(r'^(\d+)\s+(\S+)$', rest)
                if tm and tm.group(2).upper() == 'AUDIO':
                    cur_track = {
                        'track_nr': int(tm.group(1)),
                        'title': None,
                        'performer': None,
                        'index00': None,
                        'index01': None,
                    }
                    self.tracks.append(cur_track)
                else:
                    # non-audio track (e.g. a data track): ignore its indexes
                    cur_track = None

            elif cmd == 'TITLE':
                title = _unquote(rest)
                if cur_track is not None:
                    cur_track['title'] = title
                else:
                    self.album_title = title

            elif cmd == 'PERFORMER':
                performer = _unquote(rest)
                if cur_track is not None:
                    cur_track['performer'] = performer
                else:
                    self.album_performer = performer

            elif cmd == 'INDEX':
                im = re.match(r'^(\d+)\s+(\d+:\d+:\d+)$', rest)
                if im and cur_track is not None:
                    idx_nr = int(im.group(1))
                    t = _parse_index_time(im.group(2))
                    if idx_nr == 0:
                        cur_track['index00'] = t
                    elif idx_nr == 1:
                        cur_track['index01'] = t

        # keep only audio tracks that actually declared a playback start (INDEX 01)
        self.tracks = [t for t in self.tracks if t['index01'] is not None]

        if not self.tracks:
            raise CueParseError(f"No audio tracks with INDEX 01 found in {self.cue_path}")

        # INDEX times are relative to their FILE, so several files can't be
        # mapped onto the single audio file this parser splits
        if file_cnt > 1:
            raise CueParseError(f"Cue sheets referencing several files are not supported: {self.cue_path}")

        for prev, cur in zip(self.tracks, self.tracks[1:]):
            if cur['index01'] <= prev['index01']:
                raise CueParseError(f"INDEX 01 of track {cur['track_nr']} does not come after "
                                    f"track {prev['track_nr']} in {self.cue_path}")

    def track_performer(self, track):
        return track['performer'] or self.album_performer

    def track_ranges(self):
        """Yield (track, start_seconds, end_seconds) for each track in order.
        end_seconds is None for the last track (read until EOF)."""
        for i, tr in enumerate(self.tracks):
            start = tr['index01']
            end = self.tracks[i + 1]['index01'] if i + 1 < len(self.tracks) else None
            yield tr, start, end
