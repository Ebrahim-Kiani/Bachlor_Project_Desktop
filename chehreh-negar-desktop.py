import os
import requests
import subprocess
import pyautogui
import threading

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QHBoxLayout, QLineEdit, QFormLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def safe_name(name):
    return "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in name)

class OrderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Downloader")
        self.resize(950, 550)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # ---- سمت چپ: تنظیمات سرور + لیست سفارش‌ها
        left_layout = QVBoxLayout()

        # تنظیمات سرور
        server_form = QFormLayout()
        self.input_host = QLineEdit("127.0.0.1")
        self.input_port = QLineEdit("8000")
        server_form.addRow("🏠 آدرس سرور:", self.input_host)
        server_form.addRow("🔌 پورت:", self.input_port)
        left_layout.addLayout(server_form)

        self.btn_fetch = QPushButton("🔄 دریافت سفارش‌ها")
        self.btn_fetch.clicked.connect(self.fetch_orders)
        left_layout.addWidget(self.btn_fetch)

        self.label_orders = QLabel("📋 لیست سفارش‌ها:")
        left_layout.addWidget(self.label_orders)

        self.orders_list = QListWidget()
        self.orders_list.currentRowChanged.connect(self.fetch_order_details)
        left_layout.addWidget(self.orders_list)

        main_layout.addLayout(left_layout, 2)

        # ---- سمت راست: جزئیات سفارش + تصویر + پردازش
        right_layout = QVBoxLayout()
        self.label_details = QLabel("🖼 جزئیات سفارش:")
        right_layout.addWidget(self.label_details)

        self.details_list = QListWidget()
        self.details_list.currentRowChanged.connect(self.show_detail_image)
        right_layout.addWidget(self.details_list)

        self.detail_image = QLabel()
        self.detail_image.setFixedSize(300, 300)
        self.detail_image.setAlignment(Qt.AlignCenter)
        self.detail_image.setStyleSheet("border: 1px solid gray;")
        right_layout.addWidget(self.detail_image)

        self.btn_download = QPushButton("⚙️ پردازش جزئیات انتخاب شده")
        self.btn_download.clicked.connect(self.download_and_process)
        right_layout.addWidget(self.btn_download)

        main_layout.addLayout(right_layout, 3)

        # ---- داده‌ها
        self.orders = []
        self.details = []

    # ---- آدرس کامل سرور
    def server_url(self):
        host = self.input_host.text().strip()
        port = self.input_port.text().strip()
        return f"http://{host}:{port}"

    # ---- دریافت سفارش‌ها
    def fetch_orders(self):
        try:
            url = f"{self.server_url()}/order/api/orders/"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list):
                QMessageBox.warning(self, "خطا", f"داده سفارش‌ها لیست نیست:\n{data}")
                return

            self.orders = data
            self.orders_list.clear()
            for o in self.orders:
                self.orders_list.addItem(f"{o.get('id','-')} - {o.get('full_name','-')} ({o.get('status','-')})")
            QMessageBox.information(self, "موفقیت", f"✅ دریافت {len(self.orders)} سفارش موفق بود.")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در دریافت سفارش‌ها:\n{e}")
        except ValueError as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در پردازش JSON سفارش‌ها:\n{e}")

    # ---- دریافت جزئیات سفارش
    # ---- دریافت جزئیات سفارش
    def fetch_order_details(self, index):
        if index < 0 or index >= len(self.orders):
            return
        order = self.orders[index]
        order_id = order.get('id')
        if not order_id:
            return

        try:
            url = f"{self.server_url()}/order/api/order/{order_id}/details/"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            # استخراج لیست واقعی جزئیات از کلید 'details'
            details_list = data.get('details', [])
            if not isinstance(details_list, list):
                self.details_list.clear()
                self.detail_image.clear()
                QMessageBox.warning(self, "خطا", f"داده جزئیات لیست نیست:\n{details_list}")
                return

            self.details = details_list
            self.details_list.clear()
            for d in self.details:
                self.details_list.addItem(f"جزئیات {d.get('id','-')} - قیمت: {d.get('final_price','-')} تومان")

            self.detail_image.clear()
            self.detail_image.setText("📷 جزئیات را انتخاب کنید")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در دریافت جزئیات:\n{e}")
        except ValueError as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در پردازش JSON جزئیات:\n{e}")


    # ---- نمایش عکس جزئیات
    def show_detail_image(self, index):
        if index < 0 or index >= len(self.details):
            return
        detail = self.details[index]
        image_url = detail.get("image_url")
        if image_url:
            try:
                r = requests.get(image_url, timeout=5)
                r.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(r.content)
                self.detail_image.setPixmap(
                    pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            except requests.exceptions.RequestException:
                self.detail_image.setText("❌ خطا در دریافت عکس")
        else:
            self.detail_image.setText("بدون عکس")

    # ---- پردازش جزئیات انتخاب شده
    def download_and_process(self):
        order_index = self.orders_list.currentRow()
        detail_index = self.details_list.currentRow()
        if order_index < 0 or detail_index < 0:
            QMessageBox.warning(self, "خطا", "❌ هیچ سفارش یا جزئیاتی انتخاب نشده است.")
            return

        order = self.orders[order_index]
        detail = self.details[detail_index]

        order_id = order.get('id')
        user_name = safe_name(order.get('full_name', 'user'))

        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), user_name)
        os.makedirs(base_dir, exist_ok=True)

        bmp_url = detail.get('image_url')
        if not bmp_url:
            QMessageBox.warning(self, "خطا", "❌ عکس جزئیات موجود نیست.")
            return

        bmp_name = os.path.basename(bmp_url)
        bmp_file = os.path.join(base_dir, bmp_name)

        try:
            r = requests.get(bmp_url, timeout=5)
            r.raise_for_status()
            with open(bmp_file, 'wb') as f:
                f.write(r.content)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در دانلود BMP:\n{e}")
            return

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
            QMessageBox.information(self, "موفقیت", f"✅ جزئیات سفارش {detail.get('id')} پردازش شد:\n{mb4_file}")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در اجرای convert.py:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطای عمومی:\n{e}")


if __name__ == "__main__":
    app = QApplication([])
    win = OrderApp()
    win.show()
    app.exec()
