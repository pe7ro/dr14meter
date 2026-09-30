# SPDX-License-Identifier: GPL-3.0-or-later
"""The dr14meter command end to end."""

import shutil

import pytest

from helpers import ALBUM_DR, TRACKS, requires_ffmpeg, run_cli, spiky_sine, write_wav


def test_report_for_cue_album(tmp_path, wav_image):
    for f in wav_image.iterdir():
        shutil.copy(f, tmp_path)

    r = run_cli(tmp_path)
    assert r.returncode == 0, r.stderr

    lines = (tmp_path / f'dr14-DR{ALBUM_DR}.txt').read_text().splitlines()
    assert any(f'Official DR value:  DR{ALBUM_DR}' in line for line in lines)
    for title, _, dr in TRACKS:
        assert any(title in line and f'DR{dr}' in line for line in lines), title


def test_missing_path_exit_code(tmp_path):
    assert run_cli(tmp_path / 'missing').returncode == 1


@requires_ffmpeg  # the analysis commands read the title with ffprobe (see ROADMAP known issues)
@pytest.mark.parametrize('option', ['--hist', '--lev_hist', '--spectrogram', '--plot_track',
                                    '--plot_track_dst', '--dyn_vivacity', '--compress=soft'])
def test_analysis_options(tmp_path, option):
    pytest.importorskip('matplotlib')
    if option.startswith('--compress'):
        pytest.importorskip('scipy')

    # mono: --plot_track_dst used to crash on it
    track = write_wav(tmp_path / 'mono.wav', spiky_sine(0.1, channels=1, seconds=10))
    r = run_cli(option, track)
    assert r.returncode == 0 and 'Traceback' not in r.stderr, r.stderr
