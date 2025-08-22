import sys
from PyQt5.QtWidgets import QApplication
from ui_orders import OrderApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OrderApp()
    win.show()
    sys.exit(app.exec())
