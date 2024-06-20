import sys
import time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel


class MainWindow(QMainWindow):
    update_text_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )

        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 200, 20)

        screen_geometry = QtWidgets.qApp.desktop().availableGeometry()
        window_geometry = self.geometry()
        x = screen_geometry.left()
        y = screen_geometry.bottom() - window_geometry.height()
        self.setGeometry(x, y, 220, 32)

        self.update_text_signal.connect(self.update_text)

    def mousePressEvent(self, event):
        QtWidgets.qApp.quit()

    @QtCore.pyqtSlot(str)
    def update_text(self, message):
        self.label.setText(message)


class Worker(QtCore.QThread):
    update_text_signal = QtCore.pyqtSignal(str)

    def run(self):
        for x in range(10):
            message = f"Print number {x}"
            self.update_text_signal.emit(message)
            time.sleep(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()

    worker = Worker()
    worker.update_text_signal.connect(mywindow.update_text)
    worker.start()

    sys.exit(app.exec_())
