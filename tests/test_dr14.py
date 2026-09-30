# SPDX-License-Identifier: GPL-3.0-or-later
"""DR values, decoding and folder scans."""

import math

import numpy
import pytest

from dr14meter.audio_track import AudioTrack
from dr14meter.compute_dr14 import compute_dr14
from dr14meter.dynamic_range_meter import DynamicRangeMeter
from helpers import ALBUM_DR, RATE, SPIKE, TRACKS, requires_ffmpeg, spiky_sine, to_flac, write_wav


def test_sine_has_dr0():
    # the sqrt(2) RMS scaling makes a pure sine's RMS equal to its peak
    y = 0.5 * numpy.sin(2 * numpy.pi * 1000.0 * numpy.arange(20 * RATE) / RATE)
    dr, peak, rms = compute_dr14(numpy.stack([y, y], axis=1), RATE)
    assert dr == 0
    assert peak == pytest.approx(20 * math.log10(0.5), abs=0.01)
    assert rms == pytest.approx(20 * math.log10(0.5), abs=0.01)


@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('title, amplitude, expected_dr', TRACKS)
def test_known_dr(title, amplitude, expected_dr, channels):
    dr, peak, rms = compute_dr14(spiky_sine(amplitude, channels), RATE)
    assert dr == expected_dr
    assert peak == pytest.approx(20 * math.log10(SPIKE), abs=0.01)
    assert rms == pytest.approx(20 * math.log10(amplitude), abs=0.01)


@requires_ffmpeg
@pytest.mark.parametrize('channels', [1, 2, 6])
def test_wav_and_flac_decode_to_same_samples(tmp_path, channels):
    y = spiky_sine(0.1, channels)
    wav = write_wav(tmp_path / 'track.wav', y)
    flac = to_flac(wav, tmp_path / 'track.flac')

    direct, via_ffmpeg = AudioTrack(), AudioTrack()
    assert direct.open(wav) and via_ffmpeg.open(flac)
    assert direct.Fs == via_ffmpeg.Fs == RATE
    assert direct.Y.shape == via_ffmpeg.Y.shape == (len(y), channels)
    numpy.testing.assert_array_equal(direct.Y, via_ffmpeg.Y)


@pytest.mark.parametrize('album', ['wav_album', pytest.param('flac_album', marks=requires_ffmpeg)])
def test_scan_folder(album, request):
    dr = DynamicRangeMeter()
    assert dr.scan_mp(request.getfixturevalue(album), 2) == len(TRACKS)
    assert [x['dr14'] for x in dr.res_list] == [expected for _, _, expected in TRACKS]
    assert dr.dr14 == ALBUM_DR
