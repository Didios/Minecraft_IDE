# import external libraries
import vlc

from tkinter import Frame, Button, IntVar, Scale, DoubleVar, Canvas
from tkinter.messagebox import showerror

from os.path import expanduser
import time

import wave
import subprocess
from pydub import AudioSegment
from PIL import Image, ImageDraw


class Waveform(object):

    bar_count = 107
    db_ceiling = 60

    def __init__(self, filename):
        self.filename = filename
        audio_file = AudioSegment.from_file( self.filename , self.filename.split('.')[-1])

        self.peaks = self._calculate_peaks(audio_file)

    def _calculate_peaks(self, audio_file):
        """ Returns a list of audio level peaks """
        chunk_length = len(audio_file) / self.bar_count

        loudness_of_chunks = [
            audio_file[i * chunk_length: (i + 1) * chunk_length].rms
            for i in range(self.bar_count)]

        max_rms = max(loudness_of_chunks) * 1.00

        return [int((loudness / max_rms) * self.db_ceiling)
                for loudness in loudness_of_chunks]

    def _get_bar_image(self, size, fill):
        """ Returns an image of a bar. """
        width, height = size
        bar = Image.new('RGBA', size, fill)

        end = Image.new('RGBA', (width, 2), fill)
        draw = ImageDraw.Draw(end)
        draw.point([(0, 0), (3, 0)], fill='#c1c1c1')
        draw.point([(0, 1), (3, 1), (1, 0), (2, 0)], fill='#555555')

        bar.paste(end, (0, 0))
        bar.paste(end.rotate(180), (0, height - 2))
        return bar

    def _generate_waveform_image(self):
        """ Returns the full waveform image """
        im = Image.new('RGB', (840, 128), '#f5f5f5')
        for index, value in enumerate(self.peaks, start=0):
            column = index * 8 + 2
            upper_endpoint = 64 - value

            im.paste(self._get_bar_image((4, value * 2), '#424242'),
                     (column, upper_endpoint))

        return im

    def save(self):
        """ Save the waveform as an image """
        png_filename = self.filename.replace(
            self.filename.split('.')[-1], 'png')
        with open(png_filename, 'wb') as imfile:
            self._generate_waveform_image().save(imfile, 'PNG')


class Player(Frame):

    PLAY_ON_OPEN = False
    LINE_WIDTH = 3

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self._stopped = None

        self.video = expanduser('')

        # VLC player
        self.Instance = None # vlc.Instance([])
        self.player = None # self.Instance.media_player_new()

        # wave interface
        self.canvas = Canvas(self, background='#7f7f7f')
        self.canvas.bind('<Configure>', self.OnResize)
        self.peaks = []
        self.peaks_line = []
        self.line = self.canvas.create_line(-100, -100, -100, 100, fill='red')

        self.canvas.grid(row=0, column=0, sticky='nsew')

        # buttons interface
        self.buttons = Frame(self)

        # time slider
        self.timeVar = DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Scale(self.buttons, variable=self.timeVar, command=self.OnTime,
                                from_=0, to=1_000, orient='horizontal', length=500, showvalue=0)  # label='Time',
        self.timeSlider.pack(side="top", fill='x', expand=1)
        self.timeSliderUpdate = time.time()

        # play stop buttons
        self.playButton = Button(self.buttons, text="Play", command=self.OnPlay)
        self.stopButton = Button(self.buttons, text="Stop", command=self.OnStop)

        self.playButton.pack(side='left')
        self.stopButton.pack(side='left')

        # volume
        self.volVar = IntVar()
        self.volSlider = Scale(self.buttons, variable=self.volVar, command=self.OnVolume,
                               from_=0, to=100, orient='horizontal', length=200, showvalue=0, label='Volume: 50')
        self.volVar.set(50)
        self.volSlider.set(50)
        self.volSlider.pack(side='right')

        self.buttons.grid(row=1, column=0, sticky='nsew')

        self.OnTick()  # set the timer up

    def open(self, filepath):
        self.video += filepath

        # get peaks from file
        wave = Waveform(filepath)
        self.peaks = wave.peaks

        # delete ancient lines
        for i in self.peaks_line:
            self.canvas.delete(i)
        self.peaks_line = []

        # create lines for visualizer
        step = self.canvas.winfo_reqwidth() / len(wave.peaks)
        x = self.canvas.winfo_x() + step
        y = self.canvas.winfo_y() + self.canvas.winfo_reqheight() / 2
        for i in self.peaks:
            y1 = max(1, y * (i/Waveform.db_ceiling))
            self.peaks_line.append(self.canvas.create_line(x, y + y1, x, y - y1, fill='blue', width=self.LINE_WIDTH))
            x += step

        # create player
        self.Instance = vlc.Instance([])
        self.player = self.Instance.media_player_new()

        # play if option activate
        if not self.PLAY_ON_OPEN:
            self._Play(filepath)

    def OnResize(self, event):
        self._replace_lines_(event.width, event.height)

    def _replace_lines_(self, width, height):
        # space between space
        step = width / len(self.peaks)

        x = self.canvas.winfo_x() + step
        y = self.canvas.winfo_y() + height / 2

        for i, peak in enumerate(self.peaks):
            y1 = max(1, y * (peak/Waveform.db_ceiling))

            self.canvas.coords(self.peaks_line[i], x, y + y1, x, y - y1)
            x += step

        if self.player:
            x = max(1, self.player.get_time() * width / max(1, self.player.get_length()))
            self.canvas.coords(self.line, x, self.canvas.winfo_y(), x, self.canvas.winfo_y() + height)
        else:
            self.canvas.coords(self.line, 0, 0, 0, 0)

        self.canvas.tag_raise(self.line)

    def _Pause_Play(self, playing):
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self, video):
        m = self.Instance.media_new(str(video))  # Path, unicode
        self.player.set_media(m)

        self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles

    def OnPlay(self, *unused):
        """Play audio
        """
        if self.player is None:
            self.showError("There is no Video to play")
        elif not self.player.get_media():
            self._Play(self.video)
            self.video = ''
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:
            self._Pause_Play(True)

            vol = self.volVar.get()
            self.player.audio_set_volume(vol)
            vol = self.player.audio_get_volume()

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player is not None:
            self.player.stop()
            self._Pause_Play(None)
            self.timeSlider.set(0)
            self._stopped = True

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            t = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())

            if not self._stopped:
                x = max(1, self.player.get_time() * self.canvas.winfo_width() / self.player.get_length())
                y = self.canvas.winfo_reqheight()
                self.canvas.coords(self.line, x, 0, x, y)

        self.after(500, self.OnTick)

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

            if self._stopped:
                x = max(1, self.player.get_time() * self.canvas.winfo_width() / max(1, self.player.get_length()))
                y = self.canvas.winfo_reqheight()
                self.canvas.coords(self.line, x, 0, x, y)

    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = max(0, min(self.volVar.get(), 100))
        self.volSlider.config(label="Volume: " + str(vol))

        self.player.audio_set_volume(vol)

        #if self.player and not self._stopped:
        #    self.showError("Failed to set the volume: %s." % (vol,))

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.OnStop()
        showerror("Error", message)


if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    player = Player(root, bg='red')
    player.grid(row=0, column=0, sticky='nsew')
    player.open('../temp/cave1.ogg')
    root.mainloop()