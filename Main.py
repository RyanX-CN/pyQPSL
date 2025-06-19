from Tool import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QPSLMainWindow()
    main_window.show()
    sys.exit(app.exec())