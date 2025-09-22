import os
import requests
import subprocess
import pyautogui
import threading
from PyQt5.QtCore import QThread, pyqtSignal


class ProcessWorker(QThread):
    finished = pyqtSignal(str, str)   # (result, message)

    def __init__(self, order, detail, base_dir):
        super().__init__()
        self.order = order
        self.detail = detail
        self.base_dir = base_dir

    def run(self):
        try:
            bmp_url = self.detail.get("image_url")
            if not bmp_url:
                self.finished.emit("error", "❌ عکس جزئیات موجود نیست.")
                return

            bmp_name = os.path.basename(bmp_url)
            bmp_file = os.path.join(self.base_dir, bmp_name)

            # دانلود فایل
            r = requests.get(bmp_url, timeout=5)
            r.raise_for_status()
            with open(bmp_file, 'wb') as f:
                f.write(r.content)

            mb4_file = bmp_file.replace(".bmp", ".mb4")

            # شبیه‌سازی ESC بعد از ۶ ثانیه
            def press_esc():
                pyautogui.press("esc")

            timer = threading.Timer(6.0, press_esc)
            timer.start()

            subprocess.run(
                ["python", "generator.py", "-i", bmp_file, "-o", mb4_file, "-v"],
                check=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            timer.cancel()
            self.finished.emit("success", f"✅ جزئیات سفارش {self.detail.get('id')} پردازش شد:\n{mb4_file}")

        except Exception as e:
            self.finished.emit("error", f"❌ خطا در پردازش: {e}")
