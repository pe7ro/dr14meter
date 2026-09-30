# SPDX-License-Identifier: GPL-3.0-or-later

import os

import numpy
import pytest

from helpers import TRACKS, cue_text, spiky_sine, to_flac, write_wav


@pytest.fixture(scope='session', autouse=True)
def isolated_config(tmp_path_factory):
    """Keep dr14meter's config (and database settings) out of the user's home."""
    old = os.environ.get('XDG_CONFIG_HOME')
    os.environ['XDG_CONFIG_HOME'] = str(tmp_path_factory.mktemp('config'))
    yield
    if old is None:
        del os.environ['XDG_CONFIG_HOME']
    else:
        os.environ['XDG_CONFIG_HOME'] = old


@pytest.fixture(scope='session')
def wav_album(tmp_path_factory):
    """A folder with one stereo WAV per track."""
    d = tmp_path_factory.mktemp('wav_album')
    for i, (title, amplitude, _) in enumerate(TRACKS, 1):
        write_wav(d / f'{i:02d} - {title}.wav', spiky_sine(amplitude))
    return d


@pytest.fixture(scope='session')
def flac_album(tmp_path_factory, wav_album):
    d = tmp_path_factory.mktemp('flac_album')
    for wav in sorted(wav_album.glob('*.wav')):
        to_flac(wav, d / wav.with_suffix('.flac').name)
    return d


@pytest.fixture(scope='session')
def wav_image(tmp_path_factory):
    """The same album as a single WAV file plus a cue sheet."""
    d = tmp_path_factory.mktemp('wav_image')
    write_wav(d / 'Album.wav', numpy.concatenate([spiky_sine(a) for _, a, _ in TRACKS]))
    (d / 'Album.cue').write_text(cue_text('Album.wav', [t for t, _, _ in TRACKS]))
    return d


@pytest.fixture(scope='session')
def flac_image(tmp_path_factory, wav_image):
    """A single FLAC file plus cue sheet; the FLAC's own tags differ from the cue sheet."""
    d = tmp_path_factory.mktemp('flac_image')
    to_flac(wav_image / 'Album.wav', d / 'Album.flac', album='Image Tag Album', artist='Image Tag Artist')
    (d / 'Album.cue').write_text(cue_text('Album.wav', [t for t, _, _ in TRACKS]))
    return d
