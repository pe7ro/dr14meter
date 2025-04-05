import pathlib
import subprocess

import numpy as np


files_raw = pathlib.Path('sample_audio.raw')
files_wav = pathlib.Path('sample_audio.wav')
files_out = pathlib.Path('data/sample_audio_with_metadata.wav')

files_out.parent.mkdir(exist_ok=True)

# Set the seed for numpy's random number generator to ensure same results
np.random.seed(0)

sample_rate = 44100
duration = 25  # seconds

t = np.linspace(0, duration, int(sample_rate * duration), False)

pi_digits = [int(d) for d in '31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679']
audio = np.zeros_like(t)
for i, digit in enumerate(pi_digits):
    frequency = 100 + digit * 10
    amplitude = 0.1 + digit / 10
    audio += amplitude * np.sin(frequency * t * 2 * np.pi)

# Ensure that highest value is in 16-bit range
audio = audio * (2**15 - 1) / np.max(np.abs(audio))
audio = audio.astype(np.int16)

files_raw.write_bytes(audio.tobytes())

# Use ffmpeg to convert the raw file to a WAV file
subprocess.run([
    'ffmpeg',
    '-f', 's16le',
    '-ar', str(sample_rate),
    '-ac', '1',
    '-i', files_raw,
    files_wav,
])

# Use ffmpeg to add metadata to the WAV file
subprocess.run([
    'ffmpeg',
    '-i', files_wav,
    '-metadata', 'title=Sample Audio',
    '-metadata', 'artist=Generated Audio',
    '-metadata', 'album=Sample Album',
    '-metadata', 'year=2022',
    '-metadata', 'genre=Electronic',
    files_out,
])

# Remove temporary files
pathlib.Path('sample_audio.raw').unlink()
pathlib.Path('sample_audio.wav').unlink()