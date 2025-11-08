import sys
from PyQt6.QtWidgets import QApplication
from gui import WoWVendorEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WoWVendorEditor()
    window.show()
    sys.exit(app.exec())