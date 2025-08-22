import os
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QHBoxLayout, QLineEdit, QFormLayout, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from workers import ProcessWorker
from utils import safe_name


class OrderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Downloader")
        self.resize(950, 550)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # ---- سمت چپ: تنظیمات سرور + لیست سفارش‌ها
        left_layout = QVBoxLayout()
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

        # ✅ چک‌باکس ارسال به RoboExplorer
        self.robo_checkbox = QCheckBox("📤 ارسال خودکار به RoboExplorer")
        self.robo_checkbox.stateChanged.connect(self.show_robo_warning)
        right_layout.addWidget(self.robo_checkbox)

        main_layout.addLayout(right_layout, 3)

        # ---- داده‌ها
        self.orders = []
        self.details = []
        self.worker = None  # Worker Thread

    # ---- هشدار امنیتی
    def show_robo_warning(self, state):
        if state == 2:  # Checked
            QMessageBox.warning(
                self,
                "⚠️ هشدار امنیتی",
                "ارسال خودکار فایل به RoboExplorer روش امنی نیست و ممکن است باعث خطا شود.\n"
                "لطفاً مطمئن شوید RoboExplorer باز است و در مسیر صحیح قرار دارد."
            )

    # ---- آدرس کامل سرور
    def server_url(self):
        return f"http://{self.input_host.text().strip()}:{self.input_port.text().strip()}"

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
                address = o.get("address", {})
                if isinstance(address, dict):
                    full_address = address.get("full", "----")
                else:
                    full_address = str(address)
                self.orders_list.addItem(
                    f"{o.get('id','-')} - {o.get('full_name','-')} ({o.get('status','-')}) | {full_address}"
                )

            QMessageBox.information(self, "موفقیت", f"✅ دریافت {len(self.orders)} سفارش موفق بود.")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در دریافت سفارش‌ها:\n{e}")

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
            self.details = data.get("details", [])

            self.details_list.clear()
            for d in self.details:
                self.details_list.addItem(f"جزئیات {d.get('id','-')} - قیمت: {d.get('final_price','-')} تومان")

            self.detail_image.clear()
            self.detail_image.setText("📷 جزئیات را انتخاب کنید")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در دریافت جزئیات:\n{e}")

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
            except:
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

        user_name = safe_name(order.get('full_name', 'user'))
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), user_name)
        os.makedirs(base_dir, exist_ok=True)

        # اجرای Worker
        self.worker = ProcessWorker(order, detail, base_dir)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.start()

    # ---- نتیجه پردازش
    def on_process_finished(self, status, message):
        if status == "success":
            QMessageBox.information(self, "موفقیت", message)

            # ✅ اگر چک‌باکس زده شده → ارسال به RoboExplorer
            if self.robo_checkbox.isChecked():
                try:
                    from roboexplorer import send_mb4_to_robot
                    send_mb4_to_robot(message)  # فرض: message مسیر فایل MB4 است
                    QMessageBox.information(self, "RoboExplorer", "📤 فایل با موفقیت ارسال شد.")
                except Exception as e:
                    QMessageBox.warning(self, "RoboExplorer", f"❌ خطا در ارسال فایل:\n{e}")

        else:
            QMessageBox.critical(self, "خطا", message)
