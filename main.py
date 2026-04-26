import sys
from PyQt6.QtWidgets import QApplication
from Gui.main_menu import LoginWindow

print("Запуск main.py")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    sys.exit(app.exec())