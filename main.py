import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from gui import MyWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_icon = QIcon("resources/favicon.ico")
    app.setWindowIcon(app_icon)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())