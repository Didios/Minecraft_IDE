# -------------------------------------------------------------------------------
# Name:        widget_audio_player
# Purpose:     widget for sound file
#
# Author:      Didier Mathias
# Created:     24/12/2022
# Refactor:    02/05/2023
# -------------------------------------------------------------------------------

# import external libraries
import vlc

from tkinter import Frame, Button, IntVar, Scale, DoubleVar, Canvas
from tkinter.messagebox import showerror

from pydub import AudioSegment
from PIL import Image, ImageDraw

from editors.editor_widget import Editor_widget as Widget


class Waveform(object):

    bar_count = 107
    db_ceiling = 60

    def __init__(self, filename):
        self.filename = filename
        audio_file = AudioSegment.from_file(self.filename, self.filename.split('.')[-1])

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
        with open(png_filename, 'wb') as file:
            self._generate_waveform_image().save(file, 'PNG')


class Widget_audioplayer(Widget):

    PLAY_ON_OPEN = False
    LINE_WIDTH = 3

    def __init__(self, *args, **kwargs):
        filepath = kwargs.pop('filepath', None)
        Frame.__init__(self, *args, **kwargs)

        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0)

        self._stopped = None

        self.video = ''

        # VLC player
        self.Instance = None
        self.player = None

        # wave interface
        self.canvas = Canvas(self, background='#7f7f7f')
        self.canvas.bind('<Configure>', self.__OnResize)
        self.peaks = []
        self.peaks_line = []
        self.line = self.canvas.create_line(0, 0, 0, 0, fill='red')
        self.line_height = 0

        self.canvas.grid(row=0, column=0, sticky='nsew')

        # buttons interface
        self.buttons = Frame(self)

        # time slider
        self.timeVar = DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Scale(self.buttons, variable=self.timeVar, command=self.__OnTime,
                                from_=0, to=1_000, orient='horizontal', length=500, showvalue=False)
        self.timeSlider.pack(side="top", fill='x', expand=1)

        # play stop buttons
        self.playButton = Button(self.buttons, text="Play", command=self.__OnPlay)
        self.stopButton = Button(self.buttons, text="Stop", command=self.__OnStop)

        self.playButton.pack(side='left')
        self.stopButton.pack(side='left')

        # volume
        self.volVar = IntVar()
        self.volSlider = Scale(self.buttons, variable=self.volVar, command=self.__OnVolume,
                               from_=0, to=100, orient='horizontal', length=200, showvalue=False, label='Volume: 50')
        self.volVar.set(50)
        self.volSlider.set(50)
        self.volSlider.pack(side='right')

        self.buttons.grid(row=1, column=0, sticky='nsew')

        if filepath is not None:
            self.open_file(filepath)

        self.__OnTick()  # set the timer up

# region heritage

    def _modification(self, *args):
        """ set text to modify status """
        Widget._modification(self)

    def open_file(self, filepath=None):
        filepath = Widget.open_file(self, filepath)
        self.video += filepath

        # get peaks from file
        wave = Waveform(filepath)
        self.peaks = wave.peaks

        # delete ancient lines
        for i in self.peaks_line:
            self.canvas.delete(i)
        self.peaks_line = []

        # create lines for visualizer
        for _ in self.peaks:
            self.peaks_line.append(self.canvas.create_line(0, 0, 0, 0, fill='blue', width=self.LINE_WIDTH))
        self.__replace_lines(self.canvas.winfo_width(), self.canvas.winfo_height())

        # create player
        self.Instance = vlc.Instance([])
        self.player = self.Instance.media_player_new()

        # create vlc instance
        m = self.Instance.media_new(filepath)  # Path, unicode
        self.player.set_media(m)

        # play if option activate
        if self.PLAY_ON_OPEN:
            self.__OnPlay()

# endregion heritage

    def __OnResize(self, event):
        self.__replace_lines(event.width, event.height)

    def __replace_lines(self, width, height):
        # space between space
        step = width / len(self.peaks)

        x = self.canvas.winfo_x() + step
        y = self.canvas.winfo_y() + height / 2

        # sound line
        for i, peak in enumerate(self.peaks):
            y1 = max(1, y * (peak / Waveform.db_ceiling) - 10)

            self.canvas.coords(self.peaks_line[i], x, y + y1, x, y - y1)
            x += step

        # timeline
        if self.player:
            x = max(1, self.player.get_time() * width / max(1, self.player.get_length()))
            self.canvas.coords(self.line, x, 0, x, height)
        else:
            self.canvas.coords(self.line, 0, 0, 0, 0)

        self.line_height = height
        self.canvas.tag_raise(self.line)

    def __Pause_Play(self, playing):
        p = 'Pause' if playing else 'Play'
        c = self.__OnPlay if playing is None else self.__OnPause
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def __OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self.__Pause_Play(None)
            self.player.pause()  # toggles

    def __OnPlay(self, *unused):
        """Play audio
        """
        if self.player is None:
            self.showError("There is no Video to play")
        elif not self.player.get_media():
            self.showError("There is no Video to play")
            self.video = ''
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:
            self.__Pause_Play(True)

            vol = self.volVar.get()
            self.player.audio_set_volume(vol)

    def __OnStop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player is not None:
            self.player.stop()
            self.__Pause_Play(None)
            self.timeSlider.set(0)
            self._stopped = True

    def __OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            t = self.player.get_length()
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time()
                if t > 0:
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
                    self.timeVar.set(t)

            x = max(1, self.player.get_time() * self.canvas.winfo_width() / max(1, self.player.get_length()))
            self.canvas.coords(self.line, x, 0, x, self.line_height)

        self.after(20, self.__OnTick)

    def __OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                self.player.set_time(int(t))

    def __OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = max(0, min(self.volVar.get(), 100))
        self.volSlider.config(label="Volume: " + str(vol))

        self.player.audio_set_volume(vol)

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.__OnStop()
        showerror("Error", message)

# region basic function

    isModify = False

    def set_bind(self, *unused):
        pass

    def reset_binding(self, *unused):
        pass

# endregion


if __name__ == "__main__":
    from tkinter import Tk
    root = Tk()
    root.title("AUDIO TEST")

    player = Widget_audioplayer(root, bg='red', filepath='../temp/sound/cave1.ogg')
    player.grid(row=0, column=0, sticky='nsew')

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()
