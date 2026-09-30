# SPDX-License-Identifier: GPL-3.0-or-later
"""Synthetic audio with DR values known from the DR14 definition."""

import os
import pathlib
import shutil
import subprocess
import sys
import wave

import numpy
import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parents[1] / 'src'

RATE = 44100
BLOCK = 3 * (RATE + 60)  # DR14 block length at 44.1 kHz, see compute_dr14()
SECONDS = 20             # a multiple of the 1/75 s cue frame, so tracks split exactly
SPIKE = 0.8

# DR14 scales the block RMS by sqrt(2) and takes the second-highest block peak, so a sine of
# amplitude A with two spikes of height SPIKE in different blocks has DR = 20*log10(SPIKE / A)
TRACKS = [
    # title, sine amplitude, DR
    ('Dynamic', 0.1, 18),  # 20*log10(8)   = 18.06
    ('Loud', 0.5, 4),      # 20*log10(1.6) = 4.08
]
ALBUM_DR = 11              # round((18 + 4) / 2)

requires_ffmpeg = pytest.mark.skipif(
    shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None,
    reason='needs ffmpeg and ffprobe in PATH')


def spiky_sine(amplitude, channels=2, seconds=SECONDS):
    n = seconds * RATE
    y = amplitude * numpy.sin(2 * numpy.pi * 1000.0 * numpy.arange(n) / RATE)
    y[BLOCK + 1000] = SPIKE
    y[3 * BLOCK + 1000] = SPIKE
    return numpy.repeat(y[:, None], channels, axis=1)


def write_wav(path, y):
    data = numpy.round(y * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(y.shape[1])
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())
    return path


def to_flac(wav_path, flac_path, **tags):
    metadata = [arg for k, v in tags.items() for arg in ('-metadata', f'{k}={v}')]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav_path), *metadata, str(flac_path)],
                   check=True)
    return flac_path


def cue_text(audio_name, titles, seconds=SECONDS):
    lines = ['REM GENRE Classical', 'REM DATE 1999', 'PERFORMER "Test Artist"', 'TITLE "Test Album"',
             f'FILE "{audio_name}" WAVE']
    for i, title in enumerate(titles):
        mm, ss = divmod(i * seconds, 60)
        lines += [f'  TRACK {i + 1:02d} AUDIO', f'    TITLE "{title}"', f'    INDEX 01 {mm:02d}:{ss:02d}:00']
    return '\n'.join(lines) + '\n'


def run_cli(*args, cwd=None):
    env = dict(os.environ, MPLBACKEND='Agg', PYTHONWARNINGS='ignore')
    env['PYTHONPATH'] = os.pathsep.join(filter(None, [str(SRC_DIR), env.get('PYTHONPATH')]))
    return subprocess.run([sys.executable, '-m', 'dr14meter', *map(str, args)], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=300)
