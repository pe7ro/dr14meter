# SPDX-License-Identifier: GPL-3.0-or-later
"""Single-file albums with a cue sheet (issue #9)."""

import shutil

import pytest

from dr14meter.cue_sheet import CueParseError, CueSheet
from dr14meter.dynamic_range_meter import DynamicRangeMeter
from helpers import ALBUM_DR, TRACKS, cue_text, requires_ffmpeg

CUE = '''REM GENRE Classical
REM DATE 1999
PERFORMER "Test Artist"
TITLE "Test Album"
FILE "Album.flac" WAVE
  TRACK 01 AUDIO
    TITLE "Allegro"
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    TITLE "Adagio – «Largo»"
    PERFORMER "Soloist"
    INDEX 00 04:10:00
    INDEX 01 04:12:37
'''


def write_cue(folder, text, encoding='utf-8'):
    path = folder / 'Album.cue'
    path.write_bytes(text.encode(encoding))
    return path


def test_parse(tmp_path):
    cue = CueSheet(write_cue(tmp_path, CUE))
    assert (cue.album_title, cue.album_performer, cue.genre, cue.date) == \
        ('Test Album', 'Test Artist', 'Classical', '1999')

    # a track runs from its INDEX 01 to the next track's INDEX 01; the last one to the end
    ranges = list(cue.track_ranges())
    second_start = 4 * 60 + 12 + 37 / 75
    assert [(t['track_nr'], t['title'], start, end) for t, start, end in ranges] == \
        [(1, 'Allegro', 0.0, second_start), (2, 'Adagio – «Largo»', second_start, None)]
    assert [cue.track_performer(t) for t, _, _ in ranges] == ['Test Artist', 'Soloist']


@pytest.mark.parametrize('encoding', ['utf-8', 'utf-8-sig', 'utf-16', 'cp1252'])
def test_encodings(tmp_path, encoding):
    assert CueSheet(write_cue(tmp_path, CUE, encoding)).tracks[1]['title'] == 'Adagio – «Largo»'


@pytest.mark.parametrize('text', [
    CUE.replace('INDEX 01 04:12:37', 'INDEX 01 00:00:00'),
    CUE.replace('  TRACK 02', 'FILE "Other.flac" WAVE\n  TRACK 02'),
    'TITLE "No tracks"\nFILE "Album.flac" WAVE\n',
], ids=['index-not-increasing', 'several-files', 'no-tracks'])
def test_invalid(tmp_path, text):
    with pytest.raises(CueParseError):
        CueSheet(write_cue(tmp_path, text))


@pytest.mark.parametrize('image, tracks', [
    ('wav_image', 'wav_album'),
    pytest.param('flac_image', 'flac_album', marks=requires_ffmpeg),
])
def test_image_matches_separate_tracks(image, tracks, request):
    split, separate = DynamicRangeMeter(), DynamicRangeMeter()
    assert split.scan_mp(request.getfixturevalue(image), 2) == len(TRACKS)
    separate.scan_mp(request.getfixturevalue(tracks), 2)

    assert [x['file_name'] for x in split.res_list] == \
        [f'{i:02d} - {title}' for i, (title, _, _) in enumerate(TRACKS, 1)]
    assert len(split.res_list) == len(separate.res_list)
    for a, b in zip(split.res_list, separate.res_list):
        assert (a['dr14'], a['duration']) == (b['dr14'], b['duration'])
        assert a['dB_peak'] == pytest.approx(b['dB_peak'], abs=1e-6)
        assert a['dB_rms'] == pytest.approx(b['dB_rms'], abs=1e-6)
    assert split.dr14 == ALBUM_DR


@requires_ffmpeg
def test_cue_metadata_wins_over_image_tags(flac_image):
    dr = DynamicRangeMeter()
    dr.scan_mp(flac_image, 2)
    assert dr.meta_data.get_album_title() == 'Test Album'
    assert dr.meta_data.get_album_artist() == ['Test Artist']
    assert dr.meta_data.get_value('01 - Dynamic', 'title') == 'Dynamic'


def test_invalid_cue_fails_only_its_folder(tmp_path, wav_image):
    shutil.copy(wav_image / 'Album.wav', tmp_path)
    (tmp_path / 'Album.cue').write_text(cue_text('Album.wav', ['A', 'B'], seconds=0))
    dr = DynamicRangeMeter()
    assert dr.scan_mp(tmp_path, 2) == 0
    assert dr.res_list == []
