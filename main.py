from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox, QLabel, QProgressBar
from pytube import YouTube
import sys
import requests
from io import BytesIO


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super(YouTubeDownloader, self).__init__()

        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(300, 300, 600, 500)
        self.setFixedSize(600, 500)

        self.initUI()

    def initUI(self):
        self.url_label = QtWidgets.QLabel(self)
        self.url_label.setText("YouTube Video URL:")
        self.url_label.setFont(QtGui.QFont("Arial", 12))
        self.url_label.setGeometry(20, 30, 200, 30)

        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setGeometry(20, 70, 560, 30)
        self.url_input.textChanged.connect(self.update_resolutions)

        self.video_title_label = QtWidgets.QLabel(self)
        self.video_title_label.setText("")
        self.video_title_label.setFont(QtGui.QFont("Arial", 12))
        self.video_title_label.setGeometry(20, 110, 560, 30)

        self.video_thumbnail_label = QLabel(self)
        self.video_thumbnail_label.setGeometry(20, 150, 200, 150)

        self.resolution_label = QtWidgets.QLabel(self)
        self.resolution_label.setText("Select Resolution:")
        self.resolution_label.setFont(QtGui.QFont("Arial", 12))
        self.resolution_label.setGeometry(20, 310, 200, 30)

        self.resolution_combo = QComboBox(self)
        self.resolution_combo.setGeometry(20, 350, 150, 30)

        self.download_button = QtWidgets.QPushButton(self)
        self.download_button.setText("Download")
        self.download_button.setFont(QtGui.QFont("Arial", 12))
        self.download_button.setGeometry(20, 400, 100, 40)
        self.download_button.clicked.connect(self.download_video)
        self.download_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setObjectName("status_label")
        self.status_label.setText("")
        self.status_label.setFont(QtGui.QFont("Arial", 10))
        self.status_label.setGeometry(20, 450, 560, 30)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(150, 400, 400, 40)
        self.progress_bar.setValue(0)

        with open("style.css", "r", encoding="utf-8") as style_file:
            self.setStyleSheet(style_file.read())

    def update_resolutions(self):
        video_url = self.url_input.text()
        if video_url:
            try:
                yt = YouTube(video_url)
                resolutions = sorted(
                    {stream.resolution for stream in yt.streams.filter(progressive=True) if stream.resolution})
                self.resolution_combo.clear()
                self.resolution_combo.addItems(resolutions)
                self.status_label.setText(f"Available resolutions: {', '.join(resolutions)}")
                self.status_label.setStyleSheet("color: green;")

                self.video_title_label.setText(f"Title: {yt.title}")
                response = requests.get(yt.thumbnail_url)
                image = QtGui.QImage()
                image.loadFromData(BytesIO(response.content).read())
                self.video_thumbnail_label.setPixmap(QtGui.QPixmap(image).scaled(200, 150, QtCore.Qt.KeepAspectRatio))
            except Exception as e:
                self.status_label.setText(f"Error fetching resolutions: {e}")
                self.status_label.setStyleSheet("color: red;")

    def download_video(self):
        video_url = self.url_input.text()
        selected_resolution = self.resolution_combo.currentText()
        if video_url:
            save_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
            if save_path:
                try:
                    yt = YouTube(video_url)
                    stream = yt.streams.filter(res=selected_resolution, progressive=True).first()

                    if stream:
                        self.status_label.setText("Downloading...")
                        self.status_label.setStyleSheet("color: blue;")
                        yt.register_on_progress_callback(self.show_progress)
                        stream.download(save_path)
                        self.status_label.setText("Video successfully downloaded!")
                        self.status_label.setStyleSheet("color: green;")
                    else:
                        self.status_label.setText(f"Resolution {selected_resolution} not available.")
                        self.status_label.setStyleSheet("color: red;")
                except Exception as e:
                    self.status_label.setText(f"An error occurred: {e}")
                    self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setText("Please select a download directory.")
                self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setText("Please enter a valid YouTube URL.")
            self.status_label.setStyleSheet("color: red;")

    def show_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = int(bytes_downloaded / total_size * 100)
        self.progress_bar.setValue(percentage)


def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
