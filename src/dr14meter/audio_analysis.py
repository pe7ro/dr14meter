# dr14meter: compute the DR14 value of the given audio files
# Copyright (C) 2024  pe7ro
#
# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011 - 2012  Simone Riva
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

import pathlib
import tempfile
import wave
from abc import abstractmethod

import numpy

from dr14meter.audio_track import AudioTrack, StructDuration
from dr14meter.compressor import DynCompressor
from dr14meter.read_metadata import RetrieveMetadata

from dr14meter.plot.dr_histogram import compute_hist
from dr14meter.plot.lev_histogram import compute_lev_hist
from dr14meter.plot.spectrogram import spectrogram
from dr14meter.plot.dynamic_vivacity import dynamic_vivacity
from dr14meter.plot.plot_track import plot_track
from dr14meter.plot.plot_track_classic import plot_track_classic

from dr14meter.out_messages import print_msg


class AudioAnalysis:

    def compute_track(self, file_path: pathlib.Path):
        self.at = AudioTrack()

        if not self.at.open(file_path):
            return False

        self.file_name = file_path

        self.meta_data = RetrieveMetadata()
        self.meta_data.scan_file_orig(self.file_name)

        self.duration = StructDuration()
        self.duration.set_samples(self.at.Y.shape[0], self.at.Fs)

        self.virt_compute()

        return True

    def getDuration(self):
        return self.duration

    def getMetaData(self):
        return self.meta_data

    def getAudioTrack(self):
        return self.at

    def getFileName(self):
        return self.file_name

    @abstractmethod
    def virt_compute(self):
        title = self.getMetaData().get_value(self.getFileName().name, "title")
        print_msg(f"Track Title: {title} ")
        return title

    # def _virt_compute(self):


class AudioDynVivacity(AudioAnalysis):

    def virt_compute(self):
        super().virt_compute()
        at = self.getAudioTrack()
        dynamic_vivacity(at.Y, at.Fs)


class AudioDrHistogram(AudioAnalysis):

    def virt_compute(self):
        title = super().virt_compute()
        at = self.getAudioTrack()
        compute_hist(at.Y, at.Fs, self.getDuration(), title=title)


class AudioLevelHistogram(AudioAnalysis):

    def virt_compute(self):
        title = super().virt_compute()
        at = self.getAudioTrack()
        compute_lev_hist(at.Y, at.Fs, self.getDuration(), title=title)


class AudioSpectrogram(AudioAnalysis):

    def virt_compute(self):
        super().virt_compute()
        at = self.getAudioTrack()
        spectrogram(at.Y, at.Fs)


class AudioPlotTrack(AudioAnalysis):

    def virt_compute(self):
        super().virt_compute()
        at = self.getAudioTrack()
        plot_str = plot_track_classic(at.Y, at.Fs)
        plot_str.start()


class AudioPlotTrackDistribution(AudioAnalysis):

    def virt_compute(self):
        super().virt_compute()
        at = self.getAudioTrack()
        plot_track(at.Y, at.Fs)


class AudioCompressor(AudioAnalysis):

    def setCompressionModality(self, compression_modality):
        self.compression_modality = compression_modality

    def virt_compute(self):

        comp = DynCompressor()
        comp.set_compression_modality(self.compression_modality)

        full_file = pathlib.Path(tempfile.gettempdir(), f'{self.getFileName()}-compressed-.wav' )

        at = self.getAudioTrack()
        cY = comp.dyn_compressor(at.Y, at.Fs)

        wav_write(full_file, at.Fs, cY)
        print_msg(f"The resulting compressed audiotrack has been written in: {full_file}")


def wav_write(file_path, Fs, Y):
    s = Y.shape
    nchannels = s[1] if len(s) > 1 else 1
    sampwidth = 2
    framerate = int(Fs)
    nframes = s[0]
    comptype = "NONE"
    compname = "no comp"

    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

        amplitude = 2.0 ** 16 - 1.0
        Y_s = numpy.int16((amplitude / 2.0) * Y)
        Y_s = Y_s.tostring()

        wav_file.writeframes(Y_s)
