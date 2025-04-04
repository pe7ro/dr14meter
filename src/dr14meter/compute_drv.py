# dr14meter: compute the DR14 value of the given audio files
# Copyright (C) 2024  pe7ro
#
# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from dr14meter.audio_math import *

import numpy as np

# todo: why is it never used
def compute_DRV(Y, Fs, duration=None, Dr_lr=None):

    s = Y.shape

    if len(Y.shape) > 1:
        ch = s[1]
    else:
        ch = 1

    block_time = 1
    block_samples = block_time * (Fs)

    threshold = 0.15
    seg_cnt = int(np.floor(s[0] / block_samples))

    if seg_cnt < 3:
        return (0, -100, -100)

    curr_sam = 0
    rms = np.zeros((seg_cnt, ch))
    peaks = np.zeros((seg_cnt, ch))

    for i in range(seg_cnt - 1):
        r = np.arange(curr_sam, curr_sam + block_samples)

        rms[i, :] = decibel_u(u_rms(Y[r, :]), 1.0)
        peaks[i, :] = decibel_u(numpy.max(numpy.abs(Y[r, :])), 1.0)

        curr_sam = curr_sam + block_samples

    i = numpy.logical_or(rms == numpy.nan, rms == -numpy.inf)
    rms[i] = decibel_u(audio_min(), 1.0)

    i = numpy.logical_or(peaks == numpy.nan, peaks == -numpy.inf)
    peaks[i] = decibel_u(audio_min(), 1.0)

    Ydr = numpy.mean(peaks - rms, 1)

    (n, bins) = numpy.histogram(Ydr, 100)

    #print( peaks )
    #print( rms )

    max_freq = numpy.max(n)

    bs = bins.shape[0]
    bins = bins[0:bs - 1] + numpy.diff(bins) / 2.0

    i = n > max_freq * threshold

    n = n[i]
    bins = bins[i]

    m = numpy.sum(n * bins) / numpy.sum(n)

    drV = round(m - 3)

    dB_peak = numpy.max(peaks)

    dB_rms = numpy.sum(numpy.mean(rms, 0)) / 2.0

    if duration is not None:
        duration.set_samples(s[0], Fs)

    # if Dr_lr is not None:
    #     Dr_lr = ch_dr14

    return (drV, dB_peak, dB_rms)
