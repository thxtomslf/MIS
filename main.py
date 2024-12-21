import sys
from PyQt5.QtWidgets import QApplication

from start_window import StartWindow


def main():
    app = QApplication(sys.argv)
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


