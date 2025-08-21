import os
import requests
import subprocess
import pyautogui
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel

SERVER_URL = "http://127.0.0.1:8000"

def safe_name(name):
    return "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in name)

class OrderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Downloader")
        self.resize(600,400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("لیست سفارش‌ها:")
        layout.addWidget(self.label)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.btn_fetch = QPushButton("دریافت سفارش‌ها")
        self.btn_fetch.clicked.connect(self.fetch_orders)
        layout.addWidget(self.btn_fetch)

        self.btn_download = QPushButton("دانلود و پردازش سفارش انتخاب شده")
        self.btn_download.clicked.connect(self.download_and_process)
        layout.addWidget(self.btn_download)

        self.orders = []

    def fetch_orders(self):
        try:
            resp = requests.get(f"{SERVER_URL}/order/api/orders/")
            if resp.status_code==200:
                self.orders = resp.json()
                self.list_widget.clear()
                for o in self.orders:
                    self.list_widget.addItem(f"{o['id']} - {o['full_name']} - {o['status']}")
        except Exception as e:
            print("خطا در دریافت سفارش‌ها:", e)

    def download_and_process(self):
        selected = self.list_widget.currentRow()
        if selected < 0: return
        order = self.orders[selected]
        order_id = order['id']
        user_name = safe_name(order['full_name'])

        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), user_name)
        os.makedirs(base_dir, exist_ok=True)

        try:
            resp = requests.get(f"{SERVER_URL}/order/api/order/{order_id}/details/")
            if resp.status_code != 200: 
                print("جزئیات سفارش پیدا نشد")
                return
            details = resp.json()
        except Exception as e:
            print("خطا در دریافت جزئیات:", e)
            return

        for d in details:
            bmp_url = d['image_url']
            bmp_name = os.path.basename(bmp_url)
            bmp_file = os.path.join(base_dir, bmp_name)

            try:
                r = requests.get(bmp_url)
                with open(bmp_file, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print("خطا در دانلود BMP:", e)
                continue

            mb4_file = bmp_file.replace(".bmp", ".mb4")
            try:
                timer = threading.Timer(3.0, lambda: pyautogui.press("esc"))
                timer.start()

                subprocess.run(
                    ["python", "convert.py", "-i", bmp_file, "-o", mb4_file, "-v"],
                    check=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )

                timer.cancel()
                print(f"سفارش {order_id} پردازش شد: {mb4_file}")

            except subprocess.CalledProcessError as e:
                print("خطا در اجرای convert.py:", e)
            except Exception as e:
                print("خطای عمومی:", e)

if __name__=="__main__":
    app = QApplication([])
    win = OrderApp()
    win.show()
    app.exec()
