import os.path
import time
import songs
from music import Ui_MusicApp
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


class MBeats(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        # Globals
        global stopped
        global looped
        global is_shuffled

        stopped = False
        looped = False
        is_shuffled = False

        # Remove the default title bar
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Create player
        self.player = QMediaPlayer()
        self.initial_volume = 20
        self.player.setVolume(self.initial_volume)
        self.volume_dial.setValue(self.initial_volume)
        self.volume_label.setText(f'{self.initial_volume}')
        self.current_song_name.setText('No song loaded')
        self.current_song_path.setText('/')

        # Scrubbing slider timer
        self.timer = QTimer()
        self.timer.start(1000)

        # Connections

        # DEFAULT PAGE
        self.add_songs_btn.clicked.connect(self.add_song)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_resume_song)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.play_next_song)
        self.previous_btn.clicked.connect(self.play_prev_song)
        self.delete_selected_btn.clicked.connect(self.remove_song)

        self.volume_dial.valueChanged.connect(lambda: self.change_volume())

        self.timer.timeout.connect(self.move_slider)
        self.music_slider.sliderMoved[int].connect(
            lambda value: self.player.setPosition(self.music_slider.value())
        )

        # Window Movement
        self.initialPosition = self.pos()

        self.show()   # Must come before moveApp() is called

        def moveApp(event):
            if event.buttons() == Qt.LeftButton:
                self.move(
                    self.pos() + event.globalPos() - self.initialPosition
                )
                self.initialPosition = event.globalPos()
                event.accept()

        self.title_frame.mouseMoveEvent = moveApp

    def mousePressEvent(self, event):
        self.initialPosition = event.globalPos()

    # Player
    def move_slider(self):
        if stopped:
            return
        else:
            if self.player.state() == QMediaPlayer.PlayingState:
                slider_position = self.player.position()
                slider_duration = self.player.duration()
                self.music_slider.setMinimum(0)
                self.music_slider.setMaximum(self.player.duration())
                self.music_slider.setValue(slider_position)

                # update time label (continous)
                hours_pos, remainder = divmod(slider_position / 1000, 3600)
                minutes_pos, seconds_pos = divmod(remainder, 60)
                current_time = f'{int(hours_pos):02}:{int(minutes_pos):02}:{int(seconds_pos):02}'

                hours_dur, remainder = divmod(slider_duration / 1000, 3600)
                minutes_dur, seconds_dur = divmod(remainder, 60)
                song_duration = f'{int(hours_dur):02}:{int(minutes_dur):02}:{int(seconds_dur):02}'

                # current_time = time.strftime('%H:%M:%S', time.localtime(slider_position/1000))
                # song_duration = time.strftime('%H:%M:%S', time.localtime(slider_duration/1000))
                self.time_label.setText(f'{current_time} / {song_duration}')

    # Interactions
    def add_song(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            caption='Choose a song to add',
            directory=':\\',
            filter='Supported files (*.mp3; *.wav; *.ogg; *.flac; *.m4a; *.wma; *.aac; *.amr)',
        )

        if files:
            for file in files:
                songs.current_song_list.append(file)
                print(f'Added: {file}')

                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon(':/img/utils/images/MusicListItem.png'),
                        os.path.basename(file),
                    )
                )

    def remove_song(self):
        try:
            current_selection = self.loaded_songs_listWidget.currentRow()
            current_song = songs.current_song_list[current_selection]

            songs.current_song_list.remove(current_song)
            self.loaded_songs_listWidget.takeItem(current_selection)
        except Exception as e:
            print(f'Could not remove song: {e}')

    def play_song(self):
        try:
            if self.loaded_songs_listWidget.currentRow() == -1:
                current_song = songs.current_song_list[0]
                self.loaded_songs_listWidget.setCurrentRow(0)
            else:
                current_selection = self.loaded_songs_listWidget.currentRow()
                current_song = songs.current_song_list[current_selection]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()

            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')

            print(f'Currently playing: {current_song}')
        except Exception as e:
            print(f'Could not play the current song: {e}')

    def play_next_song(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]

            current_song = songs.current_song_list.index(current_song_url)
            next_song_index = (current_song + 1) % len(songs.current_song_list)
            next_song = songs.current_song_list[next_song_index]
            next_song_url = QMediaContent(QUrl.fromLocalFile(next_song))

            self.player.setMedia(next_song_url)
            self.player.play()
            self.loaded_songs_listWidget.setCurrentRow(next_song_index)

            self.current_song_name.setText(f'{os.path.basename(next_song)}')
            self.current_song_path.setText(f'{os.path.dirname(next_song)}')

            print(f'Now playing: {next_song}')
        except IndexError:
            print('Reached the last song in the list')
        except Exception as e:
            print(f'Could not play next song: {e}')

    def play_prev_song(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]

            current_song = songs.current_song_list.index(current_song_url)
            prev_song = songs.current_song_list[current_song-1]
            prev_song_url = QMediaContent(QUrl.fromLocalFile(prev_song))
            self.player.setMedia(prev_song_url)
            self.player.play()
            self.loaded_songs_listWidget.setCurrentRow(current_song-1)

            if current_song == 0:
                self.loaded_songs_listWidget.setCurrentRow(len(songs.current_song_list)-1)
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(songs.current_song_list[-1])))
                self.player.play()

            self.current_song_name.setText(f'{os.path.basename(prev_song)}')
            self.current_song_path.setText(f'{os.path.dirname(prev_song)}')            

            print(f'Now playing: {prev_song}')
        except Exception as e:
            print(f'Could not play previous song: {e}')

    def pause_and_resume_song(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop_song(self):
        try:
            self.player.stop()
        except Exception as e:
            print(f'Could not stop song: {e}')

    def change_volume(self):
        try:
            self.initial_volume = self.volume_dial.value()
            self.player.setVolume(self.initial_volume)
        except Exception as e:
            print(f'Could not control volume: {e}')
