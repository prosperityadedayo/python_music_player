import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QSlider, QLabel,
    QFileDialog, QListWidget, QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QUrl, QTime, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prosperity Music Player")
        self.setGeometry(200, 200, 600, 450)
        self.setWindowIcon(QIcon("mylogo.jpg"))

        # Media Player
        self.player = QMediaPlayer()
        self.player.setVolume(50)

        # === UI Widgets ===
        self.play_button = QPushButton("▶ Play")
        self.pause_button = QPushButton("⏸ Pause")
        self.stop_button = QPushButton("⏹ Stop")
        self.open_button = QPushButton("📂 Open Music")
        self.next_button = QPushButton("⏭ Next")
        self.prev_button = QPushButton("⏮ Previous")
        self.backward_button = QPushButton("⏪ -10s")
        self.forward_button = QPushButton("⏩ +10s")
        self.theme_button = QPushButton("Light")  # default starts in dark mode


        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        # Progress bar (seek slider)
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)

        # Labels
        self.label = QLabel("No song loaded")
        self.time_label = QLabel("00:00 / 00:00")

        # Playlist
        self.playlist = QListWidget()

        # === Layouts ===
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.next_button)

        seek_layout = QHBoxLayout()
        seek_layout.addWidget(self.backward_button)
        seek_layout.addWidget(self.progress_slider)
        seek_layout.addWidget(self.forward_button)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("Volume"))
        bottom_layout.addWidget(self.volume_slider)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.theme_button)


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.open_button)
        main_layout.addWidget(self.playlist)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(seek_layout)
        main_layout.addWidget(self.time_label)
        main_layout.addWidget(self.label)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Playlist data
        self.songs = []
        self.current_index = -1

        # === Signals ===
        self.open_button.clicked.connect(self.open_files)
        self.play_button.clicked.connect(self.play_song)
        self.pause_button.clicked.connect(self.player.pause)
        self.stop_button.clicked.connect(self.player.stop)
        self.next_button.clicked.connect(self.next_song)
        self.prev_button.clicked.connect(self.prev_song)
        self.backward_button.clicked.connect(self.seek_backward)
        self.forward_button.clicked.connect(self.seek_forward)
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        self.playlist.itemDoubleClicked.connect(self.play_selected_song)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        self.theme_button.clicked.connect(self.toggle_theme)

        # Update song progress
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.auto_next)

        # Default theme = dark
        self.dark_mode = True
        self.apply_dark_theme()

    # === Playlist Management ===
    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open Music Files", "",
            "Audio Files (*.mp3 *.wav)"
        )
        if files:
            for file in files:
                self.songs.append(file)
                self.playlist.addItem(os.path.basename(file))

            if self.current_index == -1:
                self.current_index = 0
                self.load_song(self.current_index)

    def load_song(self, index):
        if 0 <= index < len(self.songs):
            url = QUrl.fromLocalFile(self.songs[index])
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.label.setText(f"Loaded: {os.path.basename(self.songs[index])}")

    # === Controls ===
    def play_song(self):
        if self.player.mediaStatus() == QMediaPlayer.NoMedia and self.songs:
            self.load_song(self.current_index)
        self.player.play()

    def play_selected_song(self, item):
        self.current_index = self.playlist.row(item)
        self.load_song(self.current_index)
        self.play_song()

    def next_song(self):
        if self.songs:
            self.current_index = (self.current_index + 1) % len(self.songs)
            self.load_song(self.current_index)
            self.play_song()

    def prev_song(self):
        if self.songs:
            self.current_index = (self.current_index - 1) % len(self.songs)
            self.load_song(self.current_index)
            self.play_song()

    def seek_backward(self):
        new_pos = max(0, self.player.position() - 10000)  # -10s
        self.player.setPosition(new_pos)

    def seek_forward(self):
        new_pos = min(self.player.duration(), self.player.position() + 10000)  # +10s
        self.player.setPosition(new_pos)

    def seek_position(self, position):
        self.player.setPosition(position)

    # === Time + Progress ===
    def update_position(self, position):
        self.progress_slider.setValue(position)
        elapsed = QTime(0, 0).addMSecs(position)
        duration = QTime(0, 0).addMSecs(self.player.duration())
        self.time_label.setText(f"{elapsed.toString('mm:ss')} / {duration.toString('mm:ss')}")

    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)

    def auto_next(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song()

    # === Themes ===
    def toggle_theme(self):
        if self.dark_mode:
            self.apply_light_theme()
            self.theme_button.setText("Dark")   # show option to switch back
            self.dark_mode = False              # <-- important
        else:
            self.apply_dark_theme()
            self.theme_button.setText("Light")  # show option to switch again
            self.dark_mode = True               # <-- important



    def apply_dark_theme(self):
        dark_style = """
            QWidget { background-color: #121212; color: #FFD700; font-size: 14px; }
            QPushButton { background-color: #1E1E1E; border: 1px solid #FFD700; border-radius: 6px; padding: 6px; color: #FFD700; }
            QPushButton:hover { background-color: #FFD700; color: #121212; font-weight: bold; }
            QListWidget { background-color: #1A1A1A; border: 1px solid #FFD700; }
            QSlider::groove:horizontal { height: 6px; background: #333333; border-radius: 3px; }
            QSlider::handle:horizontal { background: #FFD700; border: 1px solid #FFD700; width: 14px; margin: -5px 0; border-radius: 7px; }
            QLabel { color: #FFD700; }
        """
        self.setStyleSheet(dark_style)

    def apply_light_theme(self):
        light_style = """
            QWidget { background-color: #FFFFFF; color: #000080; font-size: 14px; }
            QPushButton { background-color: #F0F0F0; border: 1px solid #000080; border-radius: 6px; padding: 6px; color: #000080; }
            QPushButton:hover { background-color: #000080; color: #FFFFFF; font-weight: bold; }
            QListWidget { background-color: #FAFAFA; border: 1px solid #000080; }
            QSlider::groove:horizontal { height: 6px; background: #CCCCCC; border-radius: 3px; }
            QSlider::handle:horizontal { background: #000080; border: 1px solid #000080; width: 14px; margin: -5px 0; border-radius: 7px; }
            QLabel { color: #000080; }
        """
        self.setStyleSheet(light_style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
