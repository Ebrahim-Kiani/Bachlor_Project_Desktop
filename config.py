import os

# آدرس سرور Django
SERVER_BASE = "http://127.0.0.1:8000"
API_ORDERS = f"{SERVER_BASE}/order/api/orders/"
API_ORDER_DETAILS = lambda order_id: f"{SERVER_BASE}/order/api/orders/{order_id}/details/"
API_MARK_DONE = lambda detail_id: f"{SERVER_BASE}/order/api/orderdetail/{detail_id}/done/"

# مسیرهای ذخیره فایل‌ها
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
CONVERTER_SCRIPT = os.path.join(BASE_DIR, "convert.py")
CONVERTER_WORKDIR = BASE_DIR

# مسیر برنامه RoboExplorer (برای بعدا)
ROBOLauncher = r"C:\Program Files\Mitsubishi Electric\RoboExplorer\RoboCom.exe"
ROBO_OPEN_TIMEOUT = 6
COORD_OPEN_BUTTON = (200, 120)
COORD_FILENAME_INPUT = (400, 300)
COORD_SEND_BUTTON = (500, 600)
