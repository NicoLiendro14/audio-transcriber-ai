import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProxyStyle, QStyle
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt


class RoundedWindow(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Real-Time Transcription")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.WIDTH = 900
        self.HEIGHT = 200
        self.resize(self.WIDTH, self.HEIGHT)

        webview = QWebEngineView()

        self.layout.addWidget(webview)
        with open("./whispersockets/index.html", "r") as f:
            html = f.read()
            f.close()

        webview.setHtml(html, QUrl("http://localhost"))


class Windows10Style(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PE_FrameWindow:
            option.rect.adjust(0, 0, -1, -1)
            super().drawPrimitive(element, option, painter, widget)
        else:
            super().drawPrimitive(element, option, painter, widget)


def setup():
    app = QApplication(sys.argv)
    app.setStyle(Windows10Style())

    window = RoundedWindow()
    window.show()

    sys.exit(app.exec_())
